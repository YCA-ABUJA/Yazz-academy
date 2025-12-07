#!/usr/bin/env python3
"""
Development server runner
"""
import os
from app import create_app

# Create application instance
app = create_app('development')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)