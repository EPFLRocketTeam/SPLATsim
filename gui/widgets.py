import tkinter as tk
from tkinter import ttk


class ParameterFrame(ttk.LabelFrame):
    """Custom frame for parameter groups with consistent styling"""
    
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, text=title, padding=10, **kwargs)
        self.row_count = 0
    
    def add_parameter(self, label_text, variable, entry_width=15, **entry_kwargs):
        """Add a labeled parameter entry to the frame"""
        ttk.Label(self, text=label_text).grid(
            row=self.row_count, column=0, sticky=tk.W, pady=2
        )
        entry = ttk.Entry(self, textvariable=variable, width=entry_width, **entry_kwargs)
        entry.grid(row=self.row_count, column=1, pady=2)
        
        self.row_count += 1
        return entry
    
    def add_parameter_hideable(self, label_text, variable, entry_width=15, **entry_kwargs):
        """Add a parameter that can be hidden/shown"""
        label = ttk.Label(self, text=label_text)
        label.grid(row=self.row_count, column=0, sticky=tk.W, pady=2)
        
        entry = ttk.Entry(self, textvariable=variable, width=entry_width, **entry_kwargs)
        entry.grid(row=self.row_count, column=1, pady=2)
        
        self.row_count += 1
        
        # Return both widgets for hide/show control
        return entry, label
    
    def add_checkbox(self, text, variable, **kwargs):
        """Add a checkbox parameter to the frame"""
        checkbox = ttk.Checkbutton(self, text=text, variable=variable, **kwargs)
        checkbox.grid(row=self.row_count, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.row_count += 1
        return checkbox
    
    def add_combobox(self, label_text, variable, values, width=12, **kwargs):
        """Add a labeled combobox to the frame"""
        ttk.Label(self, text=label_text).grid(
            row=self.row_count, column=0, sticky=tk.W, pady=2
        )
        combobox = ttk.Combobox(self, textvariable=variable, values=values, width=width, **kwargs)
        combobox.grid(row=self.row_count, column=1, pady=2)
        
        self.row_count += 1
        return combobox
    
    def add_button_row(self, buttons):
        """Add a row of buttons to the frame"""
        button_frame = ttk.Frame(self)
        button_frame.grid(row=self.row_count, column=0, columnspan=2, pady=10)
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)
        
        self.row_count += 1
        return button_frame


class ScrollableText(ttk.Frame):
    """Text widget with scrollbar"""
    
    def __init__(self, parent, height=8, width=50, **kwargs):
        super().__init__(parent)
        
        self.text = tk.Text(self, height=height, width=width, **kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def clear(self):
        """Clear all text"""
        self.text.delete(1.0, tk.END)
    
    def append(self, text):
        """Append text to the widget"""
        self.text.insert(tk.END, text)
    
    def set_text(self, text):
        """Set the text content"""
        self.clear()
        self.append(text)


class ValidationEntry(ttk.Entry):
    """Entry widget with validation"""
    
    def __init__(self, parent, variable, min_val=None, max_val=None, **kwargs):
        super().__init__(parent, textvariable=variable, **kwargs)
        
        self.variable = variable
        self.min_val = min_val
        self.max_val = max_val
        
        # Add validation
        vcmd = (self.register(self.validate), '%P')
        self.configure(validate='key', validatecommand=vcmd)
    
    def validate(self, value):
        """Validate numeric input"""
        if value == "" or value == "-":
            return True
        
        try:
            num = float(value)
            if self.min_val is not None and num < self.min_val:
                return False
            if self.max_val is not None and num > self.max_val:
                return False
            return True
        except ValueError:
            return False