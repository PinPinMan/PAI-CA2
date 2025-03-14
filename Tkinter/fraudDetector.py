import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import joblib
from ttkthemes import ThemedStyle
import re

# Enhanced Colors & Styling
COLORS = {
    'primary': "#1a73e8",
    'background': "#f8f9fa",
    'text': "#202124",
    'error': "#d93025",
    'success': "#1e8e3e"
}

# Load Model
try:
    model = joblib.load("FinalModel_DT.pkl")
except Exception as e:
    messagebox.showerror("Error", f"Failed to load model: {e}")
    model = None

# Fields and dropdown options (keeping original data)
fields = [
    'country_code', 'customer_id', 'num_orders_last_50days',
    'num_cancelled_orders_last_50days', 'num_refund_orders_last_50days',
    'total_payment_last_50days', 'num_associated_customers', 'order_id',
    'collect_type', 'order_value', 'num_items_ordered', 'refund_value',
    'payment_group'
]

dropdown_options = {
    "country_code": ['PH', 'BD', 'MY', 'PK', 'TH'],
    "collect_type": ['delivery', 'pickup'],
    "payment_group": [
        'Credit/Debit Card Payments', 'Cash/Alternative Payments', 'Digital Wallets',
        'Online Banking', 'Preloaded Balance', 'Buy Now, Pay Later', 'Other Payment Gateways'
    ]
}

# Validation Functions
def validate_order_id(order_id):
    return bool(re.match(r'^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$', order_id))

def validate_customer_id(customer_id):
    return bool(re.match(r'^[a-zA-Z0-9]{8}$', customer_id))

def validate_integer(value):
    return value.isdigit()

def validate_float(value):
    return bool(re.match(r'^\d+(\.\d{1,2})?$', value))

class SuspiciousOrderDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_style()
        self.create_header()
        self.create_main_content()
        
    def setup_window(self):
        self.root.title("SP-Buy - Suspicious Order Detector")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['background'])
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def setup_style(self):
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 28, 'bold'),
                           background=COLORS['background'],
                           foreground=COLORS['primary'])
        
        self.style.configure('SubHeader.TLabel',
                           font=('Segoe UI', 18),
                           background=COLORS['background'],
                           foreground=COLORS['text'])
        
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 11))
                           
        self.style.configure('Field.TLabel',
                           font=('Segoe UI', 10),
                           background=COLORS['background'],
                           padding=5)

    def create_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=(20,0))
        
        title = ttk.Label(header_frame, 
                         text="SP-Buy",
                         style='Header.TLabel')
        title.pack()
        
        subtitle = ttk.Label(header_frame,
                           text="Fraudulent Order Detector",
                           style='SubHeader.TLabel')
        subtitle.pack(pady=(5,20))

    def create_main_content(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        
        self.manual_tab = self.create_manual_tab()
        self.file_tab = self.create_file_tab()
        
        self.notebook.add(self.manual_tab, text="Manual Input")
        self.notebook.add(self.file_tab, text="Bulk Processing")

    def create_manual_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        
        # Center container for all content
        center_container = ttk.Frame(tab)
        center_container.pack(expand=True)  # This centers the container vertically
        
        # Main container for fields
        fields_container = ttk.Frame(center_container)
        fields_container.pack(expand=True)  # This ensures content stays centered
        
        # Create entries dictionary
        self.entries = {}
        
        # Calculate number of rows and columns
        num_columns = 2
        rows_per_column = (len(fields) + 1) // num_columns
        
        # Add spacing at the top
        spacer = ttk.Label(fields_container, text="")
        spacer.grid(row=0, column=0, columnspan=num_columns * 2, pady=10)
        
        # Create fields with original layout
        for i, field in enumerate(fields):
            col = i % num_columns
            row = (i // num_columns) + 1
            
            label = ttk.Label(fields_container, 
                            text=field.replace('_', ' ').title(),
                            style='Field.TLabel')
            label.grid(row=row, column=col * 2, sticky='e', padx=8, pady=3)
            
            if field in dropdown_options:
                entry = ttk.Combobox(fields_container,
                                   values=dropdown_options[field],
                                   width=25)
                entry.current(0)
            else:
                entry = ttk.Entry(fields_container, width=28)
            
            entry.grid(row=row, column=col * 2 + 1, padx=8, pady=5, ipady=3)
            self.entries[field] = entry
        
        # Button container for centering
        button_container = ttk.Frame(center_container)
        button_container.pack(pady=20)
        
        # Predict button
        predict_btn = ttk.Button(button_container,
                               text="Predict",
                               style='Primary.TButton',
                               command=self.single_predict)
        predict_btn.pack()
        
        return tab

    def create_file_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        
        # Center container for all content
        center_container = ttk.Frame(tab)
        center_container.pack(expand=True)
        
        instructions = ttk.Label(center_container,
                               text="Import CSV or XLSX File",
                               style='SubHeader.TLabel')
        instructions.pack(pady=20)
        
        # File input container
        file_frame = ttk.Frame(center_container)
        file_frame.pack(pady=20)
        
        self.file_entry = ttk.Entry(file_frame, width=60)
        self.file_entry.pack(side='left', padx=5)
        
        browse_btn = ttk.Button(file_frame,
                              text="📂 Browse",
                              style='Primary.TButton',
                              command=self.select_file)
        browse_btn.pack(side='left', padx=5)
        
        # Button container
        button_container = ttk.Frame(center_container)
        button_container.pack(pady=20)
        
        predict_btn = ttk.Button(button_container,
                               text="Predict",
                               style='Primary.TButton',
                               command=self.load_csv)
        predict_btn.pack()
        
        return tab

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV or XLSX", "*.csv;*.xlsx")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def preprocess_test_data(self, X_test):
        if hasattr(X_test, 'compute'):
            X_test = X_test.compute()

        X_test_processed = X_test.copy()

        country_dummies = pd.get_dummies(X_test_processed['country_code'], prefix='country_code')
        collect_type_dummies = pd.get_dummies(X_test_processed['collect_type'], prefix='collect_type')
        payment_group_dummies = pd.get_dummies(X_test_processed['payment_group'], prefix='payment_group')

        numerical_columns = [
            'num_orders_last_50days', 'num_cancelled_orders_last_50days',
            'num_refund_orders_last_50days', 'total_payment_last_50days',
            'num_associated_customers', 'order_value', 'num_items_ordered', 'refund_value'
        ]

        X_test_final = pd.concat([
            X_test_processed[numerical_columns],
            country_dummies, collect_type_dummies, payment_group_dummies
        ], axis=1)

        required_columns = [
            'num_orders_last_50days', 'num_cancelled_orders_last_50days',
            'num_refund_orders_last_50days', 'total_payment_last_50days',
            'num_associated_customers', 'order_value', 'num_items_ordered', 'refund_value',
            'country_code_MY', 'country_code_PH', 'country_code_PK', 'country_code_TH',
            'collect_type_pickup',
            'payment_group_Cash/Alternative Payments',
            'payment_group_Credit/Debit Card Payments',
            'payment_group_Digital Wallets',
            'payment_group_Online Banking',
            'payment_group_Other Payment Gateways',
            'payment_group_Preloaded Balance'
        ]

        for col in required_columns:
            if col not in X_test_final.columns:
                X_test_final[col] = 0

        X_test_final = X_test_final[required_columns]
        return X_test_final

    def load_csv(self):
        file_path = self.file_entry.get().strip()
        if not file_path:
            messagebox.showerror("Error", "Please upload a file first.")
            return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Invalid file format. Please upload CSV or XLSX.")
                return
            
            # Validate all rows before proceeding
            invalid_rows = []
            for idx, row in df.iterrows():
                if not validate_order_id(str(row['order_id'])) or not validate_customer_id(str(row['customer_id'])):
                    invalid_rows.append(idx + 2)  # +2 for 1-based index including headers
            
            if invalid_rows:
                messagebox.showerror("Error", f"Invalid Order or Customer ID format at rows: {invalid_rows}")
                return
            
            messagebox.showinfo("Success", "File validated successfully!")
            self.bulk_predict(df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def bulk_predict(self, df):
        if model is None:
            messagebox.showerror("Error", "Model is not loaded.")
            return

        try:
            # Validate order_id and customer_id inside bulk_predict()
            invalid_rows = []
            for idx, row in df.iterrows():
                if not validate_order_id(str(row['order_id'])) or not validate_customer_id(str(row['customer_id'])):
                    invalid_rows.append(idx + 2)  # +2 for correct row numbers
            
            if invalid_rows:
                messagebox.showerror("Error", f"Invalid Order or Customer ID format at rows: {invalid_rows}")
                return
            
            # Process Data
            df_processed = self.preprocess_test_data(df)
            df["is_fraud"] = model.predict(df_processed)

            # Show Results
            self.show_results(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process prediction: {e}")


    def single_predict(self):
        if model is None:
            messagebox.showerror("Error", "Model is not loaded.")
            return

        try:
            # Collect input data
            input_data = {field: self.entries[field].get().strip() for field in fields}
            
            # Validate input before processing
            errors = []
            for field, value in input_data.items():
                if not value:
                    errors.append(f"{field.replace('_', ' ').title()} cannot be empty.")
                elif field in ['num_orders_last_50days', 'num_cancelled_orders_last_50days', 'num_refund_orders_last_50days', 'num_associated_customers', 'num_items_ordered']:
                    if not validate_integer(value):
                        errors.append(f"{field.replace('_', ' ').title()} must be an integer.")
                elif field in ['total_payment_last_50days', 'order_value', 'refund_value']:
                    if not validate_float(value):
                        errors.append(f"{field.replace('_', ' ').title()} must be a number with up to 2 decimal places.")
                elif field == 'order_id' and not validate_order_id(value):
                    errors.append("Order ID must be in format 'xxxxx-xxxxx'.")
                elif field == 'customer_id' and not validate_customer_id(value):
                    errors.append("Customer ID must be 8 characters long.")

            # Show errors if any exist
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            # Convert numeric fields to correct type
            for field in ['num_orders_last_50days', 'num_cancelled_orders_last_50days', 'num_refund_orders_last_50days', 'num_associated_customers', 'num_items_ordered']:
                input_data[field] = int(input_data[field])  # Convert integers
            
            for field in ['total_payment_last_50days', 'order_value', 'refund_value']:
                input_data[field] = float(input_data[field])  # Convert to float

            # Convert input to DataFrame and preprocess
            df_input = pd.DataFrame([input_data])
            df_input_processed = self.preprocess_test_data(df_input)

            # Predict
            prediction = model.predict(df_input_processed)
            result = "Suspicious Order Detected!" if prediction[0] == 1 else "Order Appears Safe"

            messagebox.showinfo("Prediction Result", result)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to predict: {e}")



    def validate_and_predict(self):
        errors = []
        input_data = {field: self.entries[field].get().strip() for field in fields}
        for field, value in input_data.items():
            if not value:
                errors.append(f"{field.replace('_', ' ').title()} cannot be empty.")
            elif field in ['num_orders_last_50days', 'num_cancelled_orders_last_50days', 'num_refund_orders_last_50days', 'num_associated_customers', 'num_items_ordered']:
                if not validate_integer(value):
                    errors.append(f"{field.replace('_', ' ').title()} must be an integer.")
            elif field in ['total_payment_last_50days', 'order_value', 'refund_value']:
                if not validate_float(value):
                    errors.append(f"{field.replace('_', ' ').title()} must be a number with up to 2 decimal places.")
            elif field == 'order_id' and not validate_order_id(value):
                errors.append("Order ID must be in format 'xxxxx-xxxxx'.")
            elif field == 'customer_id' and not validate_customer_id(value):
                errors.append("Customer ID must be 8 characters long.")
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
        else:
            messagebox.showinfo("Success", "Input validated successfully!")
            

    def show_results(self, df):
        result_window = tk.Toplevel(self.root)
        result_window.title("Analysis Results")
        result_window.geometry("1000x600")
        result_window.configure(bg=COLORS['background'])  # Set window background
        
        # Results header with matching background
        header = ttk.Label(result_window,
                          text="Bulk Analysis Results",
                          style='Header.TLabel',
                          background=COLORS['background'])  # Match background
        header.pack(pady=20)
        
        # Table frame with matching background
        frame = ttk.Frame(result_window, style='Main.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configure the style for the frame
        self.style.configure('Main.TFrame', 
                           background=COLORS['background'])
        
        # Pagination variables
        rows_per_page = 20
        total_pages = (len(df) // rows_per_page) + (1 if len(df) % rows_per_page != 0 else 0)
        current_page = tk.IntVar(value=1)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(frame)
        x_scroll = ttk.Scrollbar(frame, orient='horizontal')
        
        # Treeview
        tree = ttk.Treeview(frame,
                           yscrollcommand=y_scroll.set,
                           xscrollcommand=x_scroll.set)
        
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        
        for col in df.columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=150, anchor='w')
        
        def load_page():
            tree.delete(*tree.get_children())
            page = current_page.get()
            start_idx = (page - 1) * rows_per_page
            end_idx = min(start_idx + rows_per_page, len(df))
            
            for i in range(start_idx, end_idx):
                values = list(df.iloc[i])
                tree.insert("", "end", values=values)
        
        # Pagination controls with matching background
        pagination_frame = ttk.Frame(result_window, style='Main.TFrame')
        pagination_frame.pack(pady=10)
        
        prev_btn = ttk.Button(pagination_frame,
                             text="<< Prev",
                             command=lambda: prev_page())
        page_label = ttk.Label(pagination_frame,
                              textvariable=current_page,
                              background=COLORS['background'])
        next_btn = ttk.Button(pagination_frame,
                             text="Next >>",
                             command=lambda: next_page())
        
        prev_btn.grid(row=0, column=0, padx=5)
        page_label.grid(row=0, column=1, padx=5)
        next_btn.grid(row=0, column=2, padx=5)

        # Pagination controls
        def prev_page():
            if current_page.get() > 1:
                current_page.set(current_page.get() - 1)
                load_page()

        def next_page():
            if current_page.get() < total_pages:
                current_page.set(current_page.get() + 1)
                load_page()
        
        # Layout
        y_scroll.pack(side='right', fill='y')
        x_scroll.pack(side='bottom', fill='x')
        tree.pack(side='left', fill='both', expand=True)
        
        load_page()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SuspiciousOrderDetector()
    app.run()


