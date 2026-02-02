# Data Directory

This directory contains structured data in YAML format that applies universally to the repository, not just to the Jekyll site.

## Structure

- `nav.yml` - Navigation menu structure
- `syllabus_modules.yml` - Course modules and topics
- `schema.sql` - PostgreSQL database schema synchronized with YAML data

## Database Synchronization

The `schema.sql` file defines a PostgreSQL database schema that mirrors the structure of the YAML data files. This allows:

1. **Relational storage**: Data can be stored in a PostgreSQL database
2. **Synchronization**: YAML files can be imported/exported to/from the database
3. **Data integrity**: Database constraints ensure data quality (minimum 4 columns, no duplicates)
4. **Canvas integration**: Supports Canvas IDs and negative IDs for unsynced items

## Usage

### Importing YAML to PostgreSQL

```bash
# Load YAML data and insert into PostgreSQL
# (Requires custom script or tool)
```

### Exporting PostgreSQL to YAML

```bash
# Export database tables to YAML format
# (Requires custom script or tool)
```

## Schema Features

- **Minimum 4 columns**: All tables enforce minimum column requirements
- **No duplicates**: Unique constraints prevent duplicate data rows
- **Canvas ID support**: Uses existing Canvas IDs or negative IDs for unsynced items
- **Auto-timestamps**: Automatic `created_at` and `updated_at` tracking
- **Referential integrity**: Foreign key constraints maintain relationships

## Data Management Rules

See `.cursor/rules/data-management-and-verification.mdc` for:
- Verification requirements for new data
- YAML format requirements
- Consolidation principles
- ID management (Canvas IDs vs negative IDs)
- Canvas synchronization guidelines