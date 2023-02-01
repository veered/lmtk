import sys
from ..utils import expand_path, printer, try_import

def has_dependencies():
  return bool(try_import('ipykernel'))

def get_kernel_manager():
  kernelspec = try_import('jupyter_client.kernelspec')
  if not kernelspec:
    return None
  return kernelspec.KernelSpecManager()

def is_kernel_installed(name):
  kernel_manager = get_kernel_manager()
  return name in kernel_manager.find_kernel_specs()

def install_kernel(name='lmtk', user=False):
  kernel_manager = get_kernel_manager()
  install_path = kernel_manager.install_kernel_spec(
    expand_path(__file__, '..', 'kernel_spec'),
    kernel_name=name,
    user=user,
  )
  return install_path

def run_install_kernel(name='lmtk', user=False):
  if not has_dependencies():
    printer.print(f"[yellow]Kernel installation failed.[/yellow]\n\nThe 'ipykernel' Python package is not installed for the version of Python located at {sys.executable}.\n\nEither install this package manually or include the 'extras' feature when installing lmtk:\n  pip install -U lmtk\[extras]")
    return False

  if is_kernel_installed(name):
    printer.print(f'Reinstalling {name} Jupyter kernel...')
  else:
    printer.print(f'Installing {name} Jupyter kernel...')

  try:
    install_path = install_kernel(name=name, user=user)
    printer.print(f'\n[green]Successfully installed {name} Jupyter kernel to[/green] {install_path}')
    return True
  except Exception as e:
    printer.print('\n[yellow]Kernel installation failed.[/yellow]')
    printer.exception(e)
    return False

if __name__ == '__main__':
  run_install_kernel()
