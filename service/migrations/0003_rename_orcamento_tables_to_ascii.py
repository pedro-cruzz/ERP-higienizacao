from django.db import migrations


def _table_exists(schema_editor, table_name):
    with schema_editor.connection.cursor() as cursor:
        tables = schema_editor.connection.introspection.table_names(cursor)
    return table_name in tables


def _table_columns(schema_editor, table_name):
    with schema_editor.connection.cursor() as cursor:
        description = schema_editor.connection.introspection.get_table_description(
            cursor,
            table_name,
        )
    return [column.name for column in description]


def rename_orcamento_schema(apps, schema_editor):
    if _table_exists(schema_editor, "service_orçamento"):
        schema_editor.execute(
            'ALTER TABLE "service_orçamento" RENAME TO "service_orcamento";'
        )

    if _table_exists(schema_editor, "service_orçamento_itens"):
        schema_editor.execute(
            'ALTER TABLE "service_orçamento_itens" RENAME TO "service_orcamento_itens";'
        )

    if _table_exists(schema_editor, "service_orcamento_itens"):
        columns = _table_columns(schema_editor, "service_orcamento_itens")
        if "orçamento_id" in columns and "orcamento_id" not in columns:
            schema_editor.execute(
                'ALTER TABLE "service_orcamento_itens" RENAME COLUMN "orçamento_id" TO "orcamento_id";'
            )


def reverse_rename_orcamento_schema(apps, schema_editor):
    if _table_exists(schema_editor, "service_orcamento_itens"):
        columns = _table_columns(schema_editor, "service_orcamento_itens")
        if "orcamento_id" in columns and "orçamento_id" not in columns:
            schema_editor.execute(
                'ALTER TABLE "service_orcamento_itens" RENAME COLUMN "orcamento_id" TO "orçamento_id";'
            )

    if _table_exists(schema_editor, "service_orcamento_itens"):
        schema_editor.execute(
            'ALTER TABLE "service_orcamento_itens" RENAME TO "service_orçamento_itens";'
        )

    if _table_exists(schema_editor, "service_orcamento"):
        schema_editor.execute(
            'ALTER TABLE "service_orcamento" RENAME TO "service_orçamento";'
        )


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0002_service_catalog_tecido_service_catalog_tempo_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    rename_orcamento_schema,
                    reverse_code=reverse_rename_orcamento_schema,
                ),
            ],
            state_operations=[
                migrations.AlterModelTable(
                    name="orcamento",
                    table="service_orcamento",
                ),
            ],
        ),
    ]
