# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScannerTypeWorkerImage'
        db.create_table(u'virusscan_scannertypeworkerimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_label', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('instance_type', self.gf('django.db.models.fields.CharField')(default='m1.medium', max_length=32)),
        ))
        db.send_create_signal(u'virusscan', ['ScannerTypeWorkerImage'])

        # Adding field 'ScannerType.worker_image'
        db.add_column(u'virusscan_scannertype', 'worker_image',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['virusscan.ScannerTypeWorkerImage']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ScannerTypeWorkerImage'
        db.delete_table(u'virusscan_scannertypeworkerimage')

        # Deleting field 'ScannerType.worker_image'
        db.delete_column(u'virusscan_scannertype', 'worker_image_id')


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
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_evilness': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'worker_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['virusscan.ScannerTypeWorkerImage']"})
        },
        u'virusscan.scannertypeworkerimage': {
            'Meta': {'object_name': 'ScannerTypeWorkerImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'instance_type': ('django.db.models.fields.CharField', [], {'default': "'m1.medium'", 'max_length': '32'})
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
            'metadata': ('djorm_hstore.fields.DictionaryField', [], {}),
            'pending': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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