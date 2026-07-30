import json
import os
from datetime import datetime
from flask import request, jsonify

class IPBlacklistMiddleware:
    def __init__(self, app, blacklist_file='blacklist_ips.json', reload_interval=60):
        self.app = app
        self.blacklist_file = blacklist_file
        self.reload_interval = reload_interval
        self.blacklisted_ips = set()
        self.last_reload = None
        self.load_blacklist()
        
        @app.before_request
        def check_ip_blacklist():
            # Reload blacklist periodically
            self.reload_if_needed()
            
            # Get real IP from Cloudflare headers
            real_ip = request.headers.get('CF-Connecting-IP') or \
                      request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
                      request.remote_addr
            
            if real_ip in self.blacklisted_ips:
                app.logger.warning(f'Blocked request from blacklisted IP: {real_ip}')
                return jsonify({"message": "Access denied"}), 403
    
    def load_blacklist(self):
        """Load blacklist from JSON file"""
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r') as f:
                    data = json.load(f)
                    self.blacklisted_ips = set(data.get('blacklisted_ips', []))
                    self.last_reload = datetime.now()
                    self.app.logger.info(f'Loaded {len(self.blacklisted_ips)} blacklisted IPs')
            else:
                self.app.logger.warning(f'Blacklist file not found: {self.blacklist_file}')
                self.blacklisted_ips = set()
                self.last_reload = datetime.now()
        except Exception as e:
            self.app.logger.error(f'Error loading blacklist: {e}')
            self.blacklisted_ips = set()
    
    def reload_if_needed(self):
        """Reload blacklist if reload_interval has passed"""
        if self.last_reload is None:
            self.load_blacklist()
            return
        
        elapsed = (datetime.now() - self.last_reload).total_seconds()
        if elapsed >= self.reload_interval:
            self.load_blacklist()
