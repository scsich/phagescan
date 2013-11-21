# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScanRunResultFileOutput'
        db.create_table(u'virusscan_scanrunresultfileoutput', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('md5', self.gf('sample.fields.Md5Field')(unique=True, max_length=32)),
            ('sha256', self.gf('sample.fields.Sha256Field')(unique=True, max_length=64)),
            ('submission_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('filename', self.gf('django.db.models.fields.CharField')(default='FILENAME_NOT_SPECIFIED', max_length=254)),
        ))
        db.send_create_signal(u'virusscan', ['ScanRunResultFileOutput'])

        # Adding model 'ScanRunResultImageOutput'
        db.create_table(u'virusscan_scanrunresultimageoutput', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('md5', self.gf('sample.fields.Md5Field')(unique=True, max_length=32)),
            ('sha256', self.gf('sample.fields.Sha256Field')(unique=True, max_length=64)),
            ('submission_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('filename', self.gf('django.db.models.fields.CharField')(default='FILENAME_NOT_SPECIFIED', max_length=254)),
        ))
        db.send_create_signal(u'virusscan', ['ScanRunResultImageOutput'])

        # Deleting field 'ScanRunResult.infected'
        db.delete_column(u'virusscan_scanrunresult', 'infected')

        # Deleting field 'ScanRunResult.infected_string'
        db.delete_column(u'virusscan_scanrunresult', 'infected_string')

        # Adding field 'ScanRunResult.task_id'
        db.add_column(u'virusscan_scanrunresult', 'task_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)

        # Adding M2M table for field file_output on 'ScanRunResult'
        db.create_table(u'virusscan_scanrunresult_file_output', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scanrunresult', models.ForeignKey(orm[u'virusscan.scanrunresult'], null=False)),
            ('scanrunresultfileoutput', models.ForeignKey(orm[u'virusscan.scanrunresultfileoutput'], null=False))
        ))
        db.create_unique(u'virusscan_scanrunresult_file_output', ['scanrunresult_id', 'scanrunresultfileoutput_id'])

        # Adding M2M table for field image_output on 'ScanRunResult'
        db.create_table(u'virusscan_scanrunresult_image_output', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scanrunresult', models.ForeignKey(orm[u'virusscan.scanrunresult'], null=False)),
            ('scanrunresultimageoutput', models.ForeignKey(orm[u'virusscan.scanrunresultimageoutput'], null=False))
        ))
        db.create_unique(u'virusscan_scanrunresult_image_output', ['scanrunresult_id', 'scanrunresultimageoutput_id'])

    def backwards(self, orm):
        # Deleting model 'ScanRunResultFileOutput'
        db.delete_table(u'virusscan_scanrunresultfileoutput')

        # Deleting model 'ScanRunResultImageOutput'
        db.delete_table(u'virusscan_scanrunresultimageoutput')

        # Adding field 'ScanRunResult.infected'
        db.add_column(u'virusscan_scanrunresult', 'infected',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'ScanRunResult.infected_string'
        raise RuntimeError("Cannot reverse this migration. 'ScanRunResult.infected_string' and its values cannot be restored.")
        # Deleting field 'ScanRunResult.task_id'
        db.delete_column(u'virusscan_scanrunresult', 'task_id')

        # Removing M2M table for field file_output on 'ScanRunResult'
        db.delete_table('virusscan_scanrunresult_file_output')

        # Removing M2M table for field image_output on 'ScanRunResult'
        db.delete_table('virusscan_scanrunresult_image_output')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sample.filesample': {
            'Meta': {'object_name': 'FileSample'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('sample.fields.Md5Field', [], {'unique': 'True', 'max_length': '32'}),
            'other_name': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sample.OtherFilename']", 'symmetrical': 'False'}),
            'sha256': ('sample.fields.Sha256Field', [], {'unique': 'True', 'max_length': '64'}),
            'submission_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'sample.otherfilename': {
            'Meta': {'object_name': 'OtherFilename'},
            'filename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '254'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'virusscan.scannertype': {
            'Meta': {'unique_together': "(('name', 'platform'),)", 'object_name': 'ScannerType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'virusscan.scanrun': {
            'Meta': {'object_name': 'ScanRun'},
            'date_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sample.FileSample']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'virusscan.scanrunresult': {
            'Meta': {'unique_together': "(('scanner_type', 'scan_run'),)", 'object_name': 'ScanRunResult'},
            'file_output': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['virusscan.ScanRunResultFileOutput']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_output': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['virusscan.ScanRunResultImageOutput']", 'symmetrical': 'False'}),
            'metadata': ('djorm_hstore.fields.DictionaryField', [], {'default': '{}'}),
            'scan_run': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['virusscan.ScanRun']"}),
            'scanner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['virusscan.ScannerType']"}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'virusscan.scanrunresultfileoutput': {
            'Meta': {'object_name': 'ScanRunResultFileOutput'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "'FILENAME_NOT_SPECIFIED'", 'max_length': '254'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('sample.fields.Md5Field', [], {'unique': 'True', 'max_length': '32'}),
            'sha256': ('sample.fields.Sha256Field', [], {'unique': 'True', 'max_length': '64'}),
            'submission_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'virusscan.scanrunresultimageoutput': {
            'Meta': {'object_name': 'ScanRunResultImageOutput'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "'FILENAME_NOT_SPECIFIED'", 'max_length': '254'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('sample.fields.Md5Field', [], {'unique': 'True', 'max_length': '32'}),
            'sha256': ('sample.fields.Sha256Field', [], {'unique': 'True', 'max_length': '64'}),
            'submission_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['virusscan']
