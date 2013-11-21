# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'ScannerType'
        db.create_table('virusscan_scannertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('platform', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('virusscan', ['ScannerType'])

        # Adding unique constraint on 'ScannerType', fields ['name', 'platform']
        db.create_unique('virusscan_scannertype', ['name', 'platform'])

        # Adding model 'ScanRun'
        db.create_table('virusscan_scanrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sample.FileSample'])),
            ('date_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='PENDING', max_length=50)),
        ))
        db.send_create_signal('virusscan', ['ScanRun'])

        # Adding model 'ScanRunResult'
        db.create_table('virusscan_scanrunresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scanner_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['virusscan.ScannerType'])),
            ('scan_run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['virusscan.ScanRun'])),
            ('infected', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('infected_string', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('traceback', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('metadata', self.gf('djorm_hstore.fields.DictionaryField')()),
        ))
        db.send_create_signal('virusscan', ['ScanRunResult'])

        # Adding unique constraint on 'ScanRunResult', fields ['scanner_type', 'scan_run']
        db.create_unique('virusscan_scanrunresult', ['scanner_type_id', 'scan_run_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'ScanRunResult', fields ['scanner_type', 'scan_run']
        db.delete_unique('virusscan_scanrunresult', ['scanner_type_id', 'scan_run_id'])

        # Removing unique constraint on 'ScannerType', fields ['name', 'platform']
        db.delete_unique('virusscan_scannertype', ['name', 'platform'])

        # Deleting model 'ScannerType'
        db.delete_table('virusscan_scannertype')

        # Deleting model 'ScanRun'
        db.delete_table('virusscan_scanrun')

        # Deleting model 'ScanRunResult'
        db.delete_table('virusscan_scanrunresult')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sample.filesample': {
            'Meta': {'object_name': 'FileSample'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('sample.fields.Md5Field', [], {'unique': 'True', 'max_length': '32'}),
            'sha256': ('sample.fields.Sha256Field', [], {'unique': 'True', 'max_length': '64'}),
            'submission_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'virusscan.scannertype': {
            'Meta': {'unique_together': "(('name', 'platform'),)", 'object_name': 'ScannerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'virusscan.scanrun': {
            'Meta': {'object_name': 'ScanRun'},
            'date_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sample.FileSample']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'virusscan.scanrunresult': {
            'Meta': {'unique_together': "(('scanner_type', 'scan_run'),)", 'object_name': 'ScanRunResult'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infected': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'infected_string': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'metadata': ('djorm_hstore.fields.DictionaryField', [], {}),
            'scan_run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['virusscan.ScanRun']"}),
            'scanner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['virusscan.ScannerType']"}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['virusscan']
