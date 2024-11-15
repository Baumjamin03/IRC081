from Pages.BasePage import *


class InfoPageClass(BasePageClass):
    def __init__(self, master):
        super().__init__(master)

        """
        Ai cooked on this one ngl
        """

        # Get git information
        import subprocess
        import datetime

        try:
            # Get latest commit hash
            version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()

            # Get commit author
            author = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%an']).decode('utf-8').strip()

            # Get commit date and format it
            date_str = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%ci']).decode('utf-8').strip()
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z').strftime('%Y-%m-%d %H:%M')

        except subprocess.CalledProcessError:
            # If git commands fail, use default values
            version = "N/A"
            author = "Unknown"
            date = "N/A"

        self.info_labels = {
            "AppName": HorizontalValueDisplay(self, "Name:", value="IRC081-Interface"),
            "Version": HorizontalValueDisplay(self, "Version:", value=version),
            "Author": HorizontalValueDisplay(self, "Author:", value=author),
            "Date": HorizontalValueDisplay(self, "Date:", value=date)
        }

        for i, label in enumerate(self.info_labels.values()):
            label.grid(row=i, column=0, sticky="nsew")
