import os
import sys

from src.MainApp import MainApp

if __name__ == "__main__":
    main_script_dir = os.path.dirname(os.path.realpath(__file__))

    app = MainApp(main_script_dir)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
