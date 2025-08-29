# Inventory Management System - Setup and Run Guide

## Prerequisites

Before running the application, make sure you have Python 3.7 or higher installed on your system.

## Step 1: Install Required Dependencies

First, you'll need to install the required Python packages. Open your terminal/command prompt and run:

```bash
pip install flask werkzeug reportlab
```

Or create a `requirements.txt` file with the following content:

```
Flask==2.3.3
Werkzeug==2.3.7
reportlab==4.0.4
```

Then install using:
```bash
pip install -r requirements.txt
```

## Step 2: Save the Code

1. Create a new directory for your project:
   ```bash
   mkdir inventory_management
   cd inventory_management
   ```

2. Save the main code as `app.py` (copy the entire code from the artifact above)

3. The application uses SQLite database, so no additional database setup is required.

## Step 3: Run the Application

1. Open terminal/command prompt in your project directory
2. Run the following command:
   ```bash
   python app.py
   ```

3. You should see output similar to:
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: off
   ```

4. Open your web browser and navigate to: `http://127.0.0.1:5000` or `http://localhost:5000`

## Step 4: First Time Setup

1. **Register a new account**: Click "Register here" on the login page
2. **Fill in your details**: Username, email, and password
3. **Login**: Use your credentials to access the system

## Application Features

### 🏠 Dashboard
- Overview of total items, stock value, and low stock alerts
- Recent transactions display
- Quick access to all modules

### 📦 Items Management (CRUD Operations)
- **Create**: Add new inventory items with details like name, category, quantity, price, supplier
- **Read**: View all items with search and filter capabilities
- **Update**: Edit existing item information
- **Delete**: Remove items (only if no transactions exist)

### 💰 Transactions
- Record stock IN (purchases, returns)
- Record stock OUT (sales, usage)
- Automatic quantity updates
- Transaction history with references

### 📊 Reports
- **Stock Level Report**: Current inventory status with low stock indicators
- **Transaction Report**: Filterable transaction history by date range
- **PDF Export**: Generate printable PDF reports for stock levels

## Directory Structure

After running, your project structure will look like:

```
inventory_management/
├── app.py                 # Main application file
├── inventory.db          # SQLite database (created automatically)
├── requirements.txt      # Dependencies (if created)
└── README.md            # This guide
```

## Default Configuration

- **Database**: SQLite (`inventory.db` - created automatically)
- **Server**: Flask development server
- **Port**: 5000
- **Debug Mode**: Disabled by default

## Customization Options

### Change Server Configuration
Edit the bottom of `app.py`:

```python
if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(
        host='127.0.0.1',    # Change to '0.0.0.0' for network access
        port=5000,           # Change port if needed
        debug=True           # Enable for development
    )
```

### Security Settings
For production use, change the secret key:

```python
app.secret_key = 'your-secure-secret-key-here'
```

### Database Location
The database file `inventory.db` is created in the same directory as your application. To change this, modify the database connection functions.

## Usage Tips

### Adding Your First Items
1. Go to Items → Add New Item
2. Fill in required fields:
   - **Name**: Product name
   - **Category**: Group items for better organization
   - **Quantity**: Current stock level
   - **Unit Price**: Price per unit
   - **Minimum Stock**: Alert threshold
   - **Supplier**: Vendor information

### Recording Transactions
1. Go to Transactions → Add Transaction
2. Select the item from dropdown
3. Choose transaction type:
   - **IN**: For purchases or stock increases
   - **OUT**: For sales or stock decreases
4. Enter quantity and current unit price
5. Add reference number and notes for tracking

### Generating Reports
1. Navigate to Reports section
2. Choose report type:
   - **Stock Report**: Current inventory levels
   - **Transaction Report**: Historical transactions
3. Use date filters for transaction reports
4. Click "Generate PDF" to download printable reports

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install flask werkzeug reportlab
```

**2. Database errors**
Delete the `inventory.db` file and restart the application to recreate the database.

**3. Permission errors**
Ensure you have write permissions in the project directory.

**4. Port already in use**
Change the port number in the `app.run()` function or stop other applications using port 5000.

### Development Mode
For development, enable debug mode:
```python
app.run(debug=True)
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

## Production Deployment

For production deployment, consider:

1. **Use a proper WSGI server**: Gunicorn, uWSGI
2. **Set up environment variables**: For secret keys and configuration
3. **Use PostgreSQL or MySQL**: Instead of SQLite for better performance
4. **Enable HTTPS**: For secure communication
5. **Set up proper logging**: For monitoring and debugging

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Database Schema

The application creates three main tables:

- **users**: User authentication
- **items**: Inventory items with details
- **transactions**: Stock movement records

All tables are created automatically when you first run the application.

## Support and Customization

This is a complete, functional inventory management system that you can customize according to your needs. The code is well-structured and documented for easy modification.

Common customizations might include:
- Adding more item fields
- Implementing barcode scanning
- Adding more report types
- Integrating with external systems
- Adding user roles and permissions