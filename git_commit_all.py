import subprocess
import os

status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8').strip().split('\n')

for line in status_output:
    if not line:
        continue
    status = line[:2]
    # Handle renames e.g. R  old_path -> new_path
    if '->' in line:
        parts = line[3:].split(' -> ')
        file_path = parts[1].strip()
        old_path = parts[0].strip()
        subprocess.run(['git', 'add', old_path, file_path])
        action = 'Rename'
    else:
        file_path = line[3:].strip()
        subprocess.run(['git', 'add', file_path])
        if status.startswith('A') or status.startswith('?'):
            action = 'Add'
        elif status.startswith('D') or status.endswith('D'):
            action = 'Remove'
        else:
            action = 'Update'
            
    # Remove quotes from filename if git added them
    file_path = file_path.strip('\"')
    base_name = os.path.basename(file_path)
    
    msg = f'{action} {base_name}'
    if file_path.endswith('.html'):
        msg = f'{action} {base_name} to reflect new structural changes'
    elif file_path.endswith('.py'):
        msg = f'{action} {base_name} logic for backend APIs'
    elif file_path.endswith('.css'):
        msg = f'{action} {base_name} styling'
    elif file_path.endswith('.md'):
        msg = f'{action} {base_name} with comprehensive details'
    elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
        msg = f'{action} {base_name} configuration'
    else:
        msg = f'{action} {base_name} for the project structure'
        
    print(f'Committing {file_path} with message: {msg}')
    subprocess.run(['git', 'commit', '-m', msg])

print("Pushing to GitHub...")
subprocess.run(['git', 'push'])
