#!/usr/bin/env python3
"""
Attack Surface Enumeration Tool
Bastet's comprehensive recon toolkit for bug bounty targets
"""

import subprocess
import json
import os
import sys
from pathlib import Path
import typer
from typing import List, Optional
import time
from datetime import datetime

app = typer.Typer(help="🐱 Bastet's Attack Surface Enumeration Tool")

def run_command(cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Execute a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        typer.echo(f"⏰ Command timed out: {' '.join(cmd)}", err=True)
        return subprocess.CompletedProcess(cmd, 1, "", "Command timed out")
    except Exception as e:
        typer.echo(f"❌ Error running command: {e}", err=True)
        return subprocess.CompletedProcess(cmd, 1, "", str(e))

def ensure_logs_dir(target: str) -> Path:
    """Ensure logs directory exists for target"""
    logs_dir = Path("/home/pierce/projects/bastet-operator/logs/surface_enum") / target
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def subdomain_discovery(domain: str, logs_dir: Path) -> List[str]:
    """Discover subdomains using multiple tools"""
    typer.echo(f"🔍 Discovering subdomains for {domain}...")
    
    subdomains = set()
    
    # Try subfinder if available
    subfinder_result = run_command(["subfinder", "-d", domain, "-silent"])
    if subfinder_result.returncode == 0:
        subdomains.update(subfinder_result.stdout.strip().split('\n'))
        with open(logs_dir / f"{domain}_subfinder.txt", "w") as f:
            f.write(subfinder_result.stdout)
    else:
        typer.echo(f"⚠️ subfinder not available or failed for {domain}")
    
    # Try assetfinder if available
    assetfinder_result = run_command(["assetfinder", domain])
    if assetfinder_result.returncode == 0:
        subdomains.update(assetfinder_result.stdout.strip().split('\n'))
        with open(logs_dir / f"{domain}_assetfinder.txt", "w") as f:
            f.write(assetfinder_result.stdout)
    else:
        typer.echo(f"⚠️ assetfinder not available or failed for {domain}")
    
    # Manual DNS discovery using common subdomains
    common_subs = [
        "www", "api", "app", "mobile", "admin", "portal", "dashboard", 
        "dev", "test", "staging", "beta", "demo", "mail", "ftp", 
        "cdn", "static", "assets", "media", "images", "upload",
        "secure", "login", "auth", "oauth", "sso", "accounts",
        "support", "help", "docs", "blog", "news", "store"
    ]
    
    manual_subs = []
    for sub in common_subs:
        test_domain = f"{sub}.{domain}"
        # Simple DNS lookup test
        nslookup_result = run_command(["nslookup", test_domain])
        if nslookup_result.returncode == 0 and "NXDOMAIN" not in nslookup_result.stdout:
            manual_subs.append(test_domain)
            subdomains.add(test_domain)
    
    with open(logs_dir / f"{domain}_manual_subs.txt", "w") as f:
        f.write('\n'.join(manual_subs))
    
    # Remove empty strings and sort
    final_subs = sorted([s for s in subdomains if s.strip()])
    
    with open(logs_dir / f"{domain}_all_subdomains.txt", "w") as f:
        f.write('\n'.join(final_subs))
    
    typer.echo(f"✅ Found {len(final_subs)} subdomains for {domain}")
    return final_subs

def web_service_discovery(subdomains: List[str], domain: str, logs_dir: Path) -> dict:
    """Discover live web services using httpx"""
    typer.echo(f"🌐 Probing web services for {domain}...")
    
    # Write subdomains to temp file for httpx
    subs_file = logs_dir / f"{domain}_subs_input.txt"
    with open(subs_file, "w") as f:
        f.write('\n'.join(subdomains))
    
    # Try httpx if available
    httpx_cmd = [
        "httpx", "-l", str(subs_file), "-silent", "-json",
        "-title", "-tech-detect", "-status-code", "-content-length",
        "-web-server", "-ip", "-cdn", "-location"
    ]
    
    httpx_result = run_command(httpx_cmd)
    web_services = {}
    
    if httpx_result.returncode == 0:
        # Parse JSON output
        for line in httpx_result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    service = json.loads(line)
                    url = service.get('url', '')
                    web_services[url] = service
                except json.JSONDecodeError:
                    continue
        
        # Save raw httpx output
        with open(logs_dir / f"{domain}_httpx.json", "w") as f:
            f.write(httpx_result.stdout)
    else:
        typer.echo(f"⚠️ httpx not available or failed for {domain}")
        # Fallback: basic curl check
        for subdomain in subdomains[:20]:  # Limit to first 20 for manual check
            for scheme in ["https", "http"]:
                url = f"{scheme}://{subdomain}"
                curl_result = run_command(["curl", "-s", "-I", "-m", "10", url])
                if curl_result.returncode == 0 and "HTTP" in curl_result.stdout:
                    web_services[url] = {
                        "url": url,
                        "status_code": "unknown",
                        "method": "curl",
                        "headers": curl_result.stdout
                    }
    
    # Save processed web services
    with open(logs_dir / f"{domain}_web_services.json", "w") as f:
        json.dump(web_services, f, indent=2)
    
    typer.echo(f"✅ Found {len(web_services)} live web services for {domain}")
    return web_services

def interesting_endpoints(web_services: dict, domain: str, logs_dir: Path) -> dict:
    """Discover interesting endpoints and paths"""
    typer.echo(f"🔎 Discovering interesting endpoints for {domain}...")
    
    interesting_paths = [
        "/.well-known/security.txt",
        "/robots.txt",
        "/sitemap.xml", 
        "/admin",
        "/api",
        "/graphql",
        "/swagger",
        "/docs",
        "/.env",
        "/config",
        "/debug",
        "/health",
        "/status",
        "/version"
    ]
    
    findings = {}
    
    for url, service_info in list(web_services.items())[:10]:  # Limit to top 10 services
        base_url = url.rstrip('/')
        typer.echo(f"  Checking paths on {base_url}...")
        
        service_findings = {}
        
        for path in interesting_paths:
            test_url = f"{base_url}{path}"
            curl_result = run_command([
                "curl", "-s", "-I", "-m", "5", 
                "-H", "User-Agent: Bastet-Security-Scanner/1.0",
                test_url
            ])
            
            if curl_result.returncode == 0:
                headers = curl_result.stdout
                if "200 OK" in headers or "301 " in headers or "302 " in headers:
                    service_findings[path] = {
                        "url": test_url,
                        "headers": headers,
                        "timestamp": datetime.now().isoformat()
                    }
        
        if service_findings:
            findings[base_url] = service_findings
    
    # Save interesting findings
    with open(logs_dir / f"{domain}_interesting_endpoints.json", "w") as f:
        json.dump(findings, f, indent=2)
    
    typer.echo(f"✅ Found interesting endpoints on {len(findings)} services")
    return findings

@app.command()
def enumerate(
    target: str = typer.Argument(..., help="Target domain to enumerate"),
    full: bool = typer.Option(False, "--full", help="Run full enumeration (slower)"),
    skip_subs: bool = typer.Option(False, "--skip-subs", help="Skip subdomain discovery"),
    skip_web: bool = typer.Option(False, "--skip-web", help="Skip web service discovery"),
    skip_paths: bool = typer.Option(False, "--skip-paths", help="Skip path discovery")
):
    """🐱 Enumerate attack surface for a target domain"""
    
    typer.echo(f"🎯 Starting attack surface enumeration for: {target}")
    typer.echo(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    # Ensure logs directory
    logs_dir = ensure_logs_dir(target)
    typer.echo(f"📁 Logs will be saved to: {logs_dir}")
    
    results = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "subdomains": [],
        "web_services": {},
        "interesting_endpoints": {}
    }
    
    # Phase 1: Subdomain Discovery
    if not skip_subs:
        subdomains = subdomain_discovery(target, logs_dir)
        results["subdomains"] = subdomains
    else:
        # Try to load existing subdomains
        subs_file = logs_dir / f"{target}_all_subdomains.txt"
        if subs_file.exists():
            subdomains = subs_file.read_text().strip().split('\n')
            results["subdomains"] = subdomains
        else:
            subdomains = [target]  # Fallback to just the main domain
    
    # Phase 2: Web Service Discovery  
    if not skip_web and subdomains:
        web_services = web_service_discovery(subdomains, target, logs_dir)
        results["web_services"] = web_services
    else:
        web_services = {}
    
    # Phase 3: Interesting Endpoint Discovery
    if not skip_paths and web_services:
        interesting = interesting_endpoints(web_services, target, logs_dir)
        results["interesting_endpoints"] = interesting
    
    # Save comprehensive results
    with open(logs_dir / f"{target}_complete_enumeration.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate summary
    typer.echo("\n" + "="*60)
    typer.echo(f"🎯 ENUMERATION SUMMARY FOR {target.upper()}")
    typer.echo("="*60)
    typer.echo(f"📊 Subdomains discovered: {len(results['subdomains'])}")
    typer.echo(f"🌐 Live web services: {len(results['web_services'])}")
    typer.echo(f"🔍 Services with interesting endpoints: {len(results['interesting_endpoints'])}")
    typer.echo(f"📁 All data saved to: {logs_dir}")
    
    if results['interesting_endpoints']:
        typer.echo("\n🎯 INTERESTING FINDINGS:")
        for service, endpoints in results['interesting_endpoints'].items():
            typer.echo(f"  🌐 {service}")
            for path in endpoints.keys():
                typer.echo(f"    └─ {path}")
    
    typer.echo("\n✅ Enumeration complete!")

if __name__ == "__main__":
    app()
