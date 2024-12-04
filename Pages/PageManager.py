from Pages.Numpad import *
from Pages.BasePage import *


class PageManagerClass(BasePageClass):
    def __init__(self,
                 master: any,
                 lbl_page: ctk.CTkLabel,
                 **kwargs: any):
        super().__init__(master, **kwargs)
        self.current_page = None
        self.pages = {}
        self.lbl_page = lbl_page
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_page("Numpad", NumpadPageClass(self))

    def add_page(self,
                 page_name: str,
                 page) -> None:
        """
        Add a page to the manager
        """
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")
        if not self.current_page:
            self.current_page = page_name

    def show_page(self,
                  page_name: str) -> None:
        """Switch to a specific page"""
        if page_name in self.pages:
            # Notify current page it's being hidden
            if self.current_page and hasattr(self.pages[self.current_page], "on_page_leave"):
                self.pages[self.current_page].on_page_leave()

            # Show new page
            self.pages[page_name].lift()
            self.current_page = page_name

            # Notify new page it's being shown
            if hasattr(self.pages[page_name], "on_page_enter"):
                self.pages[page_name].on_page_enter()

            self.lbl_page.configure(text=page_name)

    def show_numpad(self,
                    entry: ctk.CTkEntry,
                    caller_page) -> None:
        self.pages["Numpad"].show(entry, caller_page)
