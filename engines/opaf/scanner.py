
from engines.generic.abstract import AbstractMDEngine, L32_PLATFORM
from engines.generic.exception import UnsupportedFileTypeForScanner

# output files
OUTPUT_XML 	= 'output.xml'
OUTPUT_GEXF = 'output.gexf'


class opaf_engine(AbstractMDEngine):

	# class variables
	suspicious_types = [	'JS',
							'JavaScript',
							# 'AA',
							'OpenAction',
							'AcroForm',
							'JBIG2Decode',
							'RichMedia',
							'Launch',
							'EmbeddedFile',
							'Color',
							]

	def __init__(self, engine_path=None):
		super(opaf_engine, self).__init__()
		self._engine_path = engine_path
		self._temp_dir = None
		self.output = {'result': ''}
		self._name = 'OPAF'
		self._platform = L32_PLATFORM

	def _import_opaf(self):
		import opaflib as ol
		self.__opaf_lib = ol
		# remove useless file logging from opaf
		map(self.__opaf_lib.logger.parent.removeHandler, self.__opaf_lib.logger.parent.handlers)

	@property
	def _opaf_lib(self):
		if not hasattr(self, '__opaf_lib'):
			self._import_opaf()
		return self.__opaf_lib

	def engine_path_exists(self):
		try:
			self._import_opaf()
			return True
		except ImportError:
			return False

	@property
	def supported_file_types(self):
		return ['application/pdf']

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		"""
		# OPAF does not appear to be capable of reporting its version number.
		return {'engine': ''}

	def _generate_gexf(self, xml):

		import networkx

		# DiGraph:
		# - is the base class for directed graphs
		# - stores nodes, edges, optional attributes
		# - self-loops allowed, parallel edges not allowed
		# - nodes are arbitrary hashable Python objects, optional key/value attributes
		# - edges are links between nodes, optional key/value attributes
		G = networkx.DiGraph()

		indirect_objects = self._opaf_lib.getIndirectObjectsDict(xml)

		# add nodes to the DiGraph
		G.add_nodes_from(map(str, indirect_objects.keys()))

		# add edges to the DiGraph (x -> r)
		for x in indirect_objects.keys():
			for r in indirect_objects[x].xpath(".//R"):
				G.add_edge(str(x), str(self._opaf_lib.payload(r)))

			# TODO: populate all PDF attributes for later display via mouseovers in sigma.js
			#G.node[x]['pdf_attributes'] = {}

			# 'suspicious' nodes are those that contain a blacklisted Obj type, e.g. "JavaScript" (colored Red)
			suspicious = False

			for suspicious_type in self.suspicious_types:
				for t in indirect_objects[x].xpath('dictionary/dictionary_entry/name[translate(dec(@payload), "ABCDEFGHJIKLMNOPQRSTUVWXYZ", "abcdefghjiklmnopqrstuvwxyz")="' + suspicious_type.lower() + '"]'):

					# TODO: flag /Colors > 2^24
					if suspicious_type == "Color": pass

					suspicious = True
					G.node[x]['Suspicious Attribute'] = "/" + suspicious_type
					break

			G.node[x]['suspicious'] = suspicious

		# add the root node as the end of the edge from "trailer"
		try:
			root = self._opaf_lib.getRoot(xml)
			G.add_edge("trailer", str(self._opaf_lib.payload(root)))

		# the below exception handling is from opaf itself (it doesn't get any more specific)
		except Exception, e: pass

		# TODO: can stream this graph via generate_gexf
		return str(networkx.readwrite.gexf.GEXFWriter(G))

	def _custom_do_everything(self, xml):
		"""
		Does everything that calling opaf.py directly should do.  Reimplemented here in order to allow us to add in
		exceptions and handlers for them.
		"""

		# get all indirect objects
		indirect_objects = self._opaf_lib.getIndirectObjectsDict(xml)

		# resolve all references
		for ref in self._opaf_lib.getUnresolvedRefs(xml):
			self._opaf_lib.resolvRef(xml, ref, iobjects=indirect_objects)

		# get all filtered Streams
		indirect_streams = self._opaf_lib.getFilteredStreams(xml)

		# expand all compresed streams (this will replace the node with the expanded version)
		for indirect_stream in indirect_streams:
			self._opaf_lib.expand(indirect_stream)

		# get all "Objectstream" / "ObjStm" streams
		indirect_object_streams = self._opaf_lib.getStreamsOfType(xml, 'ObjStm')

		# expand all object streams (this will replace the object streams with their expanded counterparts)
		for indirect_object_stream in indirect_object_streams:
			self._opaf_lib.expandObjStm(indirect_object_stream)

		# get all indirect objects (again)
		# we do this again because the list is updated after expanding ObjStm
		indirect_objects = self._opaf_lib.getIndirectObjectsDict(xml)

		# Since we don't filter out non-PDFs, there's a chance that OPAF interprets a non-PDF as a PDF and proceeds
		# as normal.  If this is the case, then we likely have very few indirect objects.  We raise an exception.
		if 0 == len(indirect_objects):
			raise UnsupportedFileTypeForScanner()

		# resolve all references (again)
		for ref in self._opaf_lib.getUnresolvedRefs(xml):
			self._opaf_lib.resolvRef(xml, ref, iobjects=indirect_objects)

	def _custom_multiparser_get_xml(self, pdf):
		"""
		Try all OPAF parsing strategies in some preference order in order to avoid dying so easily.
		"""
		# fallback chain of different type of parsing algorithms
		for parse_func in [self._opaf_lib.normalParser, self._opaf_lib.bruteParser, self._opaf_lib.xrefParser]:
			try:
				result = parse_func(pdf)
				if result is not None:
					return result

			# TODO: narrow this except catcher to ones that opaf is known to produce
			except:
				pass

		# none of OPAF's parsing algorithms were able to help us
		raise UnsupportedFileTypeForScanner()

	def _custom_get_stats(self, xml):
		indirect_object_count = len(xml.xpath('//*[ starts-with(local-name(),"indirect_object")] '))
		types_count = {}
		# TODO: likely incorrect matching; we need to do dec() on @payload and do case-insensitive matching to "Type"
		for ty in [self._opaf_lib.payload(x) for x in xml.xpath('//*[starts-with(local-name(),"indirect_object")]/dictionary/dictionary_entry/name[@payload=enc("Type")]/../*[position()=2]')]:
			types_count[ty] = types_count.get(ty,0)+1

		object_filter_frequencies = {}
		# TODO: likely incorrect matching; we need to do dec() on @payload and do case-insensitive matching to "Filter"
		for ty in [self._opaf_lib.payload(x) for x in xml.xpath('//indirect_object_stream/dictionary/dictionary_entry/name[@payload=enc("Filter")]/../*[position()=2]')]:
			object_filter_frequencies[ty + " filter"] = object_filter_frequencies.get(ty,0)+1

		return indirect_object_count, types_count, object_filter_frequencies

	def _make_metadata_from_opaf_stats_output(	self,
												indirect_object_count,
												types_count_dict,
												object_filter_frequencies_dict):

		d = {'indirect object': indirect_object_count}
		d.update(types_count_dict)
		d.update(object_filter_frequencies_dict)
		return d

	def _scan(self, file_object):

		from lxml import etree

		# exhaust OPAF's parsing functions in an attempt to extract a DOM from the PDF
		xml = self._custom_multiparser_get_xml(file_object.all_content)
		xml_str = etree.tostring(xml)

		# effectively the same thing as calling opaf.py on the command line, but broken out so we can add exceptions
		self._custom_do_everything(xml)

		# build the gexf (string that remains in memory; never touched disk)
		gexf = self._generate_gexf(xml)

		# handle these as files since they can both get pretty big and ARE NOT okay to store in DB
		self.add_output_file_from_string(gexf, 		original_filename=OUTPUT_GEXF)
		self.add_output_file_from_string(xml_str, 	original_filename=OUTPUT_XML)

		# take opaf stats and save them to metadata ... figure out how to use later
		stats = self._make_metadata_from_opaf_stats_output(*self._custom_get_stats(xml))
		self.output.update(stats)

		# done
		return self.output

	def _parse_scan_result(self, scan_result):
		files, images, metadata = self._output_files, self._output_images, scan_result
		metadata.update(self.version)
		return files, images, metadata


