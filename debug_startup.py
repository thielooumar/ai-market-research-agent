import sys, os

print('--- Debug startup checks ---')
print('PYTHONPATH:', os.getenv('PYTHONPATH'))
print('sys.path:', sys.path)

# Verify static directory exists
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
print('Checking static directory at', static_dir)
if not os.path.isdir(static_dir):
    raise RuntimeError(f'Static directory not found at {static_dir}')
else:
    print('Static directory exists, contains:', os.listdir(static_dir))

# Verify that the application package can be imported
try:
    import app.tools
    print('Import app.tools succeeded')
except Exception as e:
    print('Import app.tools failed:', e)
    raise

print('--- End of debug checks ---')
