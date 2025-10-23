import os
import glob
from django.core.management.base import BaseCommand, CommandError
from pymongo import MongoClient


class Command(BaseCommand):
    help = 'Import Markdown files into MongoDB wiki collection. Filenames become titles.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, required=True, help='Directory containing .md files')
        parser.add_argument('--mongo', type=str, default='mongodb://localhost:27017', help='Mongo URI')
        parser.add_argument('--db', type=str, default='minecraft', help='Mongo database name')
        parser.add_argument('--collection', type=str, default='wiki', help='Mongo collection name')

    def handle(self, *args, **options):
        directory = options['path']
        if not os.path.isdir(directory):
            raise CommandError(f'Path not found: {directory}')

        client = MongoClient(options['mongo'])
        db = client[options['db']]
        col = db[options['collection']]
        col.create_index('title', unique=True)

        md_files = glob.glob(os.path.join(directory, '*.md'))
        if not md_files:
            self.stdout.write(self.style.WARNING('No .md files found.'))
            return

        imported = 0
        for md_path in md_files:
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                filename = os.path.basename(md_path)
                title = os.path.splitext(filename)[0]

                col.update_one(
                    { 'title': title },
                    { '$set': { 'title': title, 'content': content } },
                    upsert=True
                )
                imported += 1
                self.stdout.write(self.style.SUCCESS(f'Imported: {title}'))
            except Exception as exc:
                self.stderr.write(f'Failed to import {md_path}: {exc}')

        self.stdout.write(self.style.SUCCESS(f'Done. Imported/updated {imported} documents.'))

