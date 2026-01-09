from ipykernel.kernelapp import IPKernelApp
from .kernel import SiPyKernel

def main():
    IPKernelApp.launch_instance(kernel_class=SiPyKernel)

if __name__ == "__main__":
    main()