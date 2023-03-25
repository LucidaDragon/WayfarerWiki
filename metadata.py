SITE_NAME = "Wayfarer Wiki"

import io, pathlib, xml.etree.ElementTree

class InternalPage:
	def __init__(self, virtual_path: pathlib.Path, content: bytes) -> None:
		self.virtual_path = virtual_path
		self.content = content
		self.stem = virtual_path.stem
		self.name = virtual_path.name

	def open(self, *args): return io.BytesIO(self.content)
	def __str__(self) -> str: return str(self.virtual_path)

def delete_path(path: pathlib.Path):
	if path.is_dir():
		for entry in path.iterdir(): delete_path(entry)
		path.rmdir()
	elif path.is_file():
		path.unlink()

def process_page(entry: pathlib.Path, output: pathlib.Path):
	name = entry.stem
	if len(name) > 1: name = name[0].upper() + name[1:]

	with entry.open("rb") as stream:
		document = xml.etree.ElementTree.parse(stream)
	root = document.getroot()

	head = root.find("head")
	if head == None:
		head = xml.etree.ElementTree.Element("head")
		root.insert(0, head)
	
	body = root.find("body")
	if body == None: return

	opening_paragraph = body.find("p")
	opening_image = body.find("img")

	head.clear()

	charset = xml.etree.ElementTree.Element("meta", { "charset": "utf-8" })
	head.append(charset)

	title = xml.etree.ElementTree.Element("title")
	title.text = name + " - " + SITE_NAME
	head.append(title)

	og_title = xml.etree.ElementTree.Element("meta", { "name": "og:title", "content": name })
	head.append(og_title)

	og_site_name = xml.etree.ElementTree.Element("meta", { "name": "og:site_name", "content": SITE_NAME })
	head.append(og_site_name)

	og_type = xml.etree.ElementTree.Element("meta", { "name": "og:type", "content": "article" })
	head.append(og_type)

	author = xml.etree.ElementTree.Element("meta", { "name": "author", "content": "Lucida Dragon" })
	head.append(author)

	article_author = xml.etree.ElementTree.Element("meta", { "name": "article:author", "content": "Lucida Dragon" })
	head.append(article_author)

	if opening_paragraph != None and opening_paragraph.text != None:
		head.append(xml.etree.ElementTree.Element("meta", { "name": "description", "content": opening_paragraph.text }))
		head.append(xml.etree.ElementTree.Element("meta", { "name": "og:description", "content": opening_paragraph.text }))
	
	if opening_image != None and "src" in opening_image.attrib:
		head.append(xml.etree.ElementTree.Element("meta", { "name": "og:image", "content": opening_image.attrib["src"] }))

	style = xml.etree.ElementTree.Element("link", { "rel": "stylesheet", "href": "global.css" })
	head.append(style)

	script = xml.etree.ElementTree.Element("script", { "src": "global.js" })
	head.append(script)
	with output.joinpath("./" + entry.name).open("wb") as stream: stream.write(get_html_bytes(root))

def get_html_bytes(element: xml.etree.ElementTree.Element):
	return "<!DOCTYPE html>\r\n".encode("UTF-8") + xml.etree.ElementTree.tostring(element, method="html")

def create_index(pages: list[pathlib.Path], root: pathlib.Path) -> pathlib.Path:
	index = xml.etree.ElementTree.Element("html")
	body = xml.etree.ElementTree.Element("body")
	header = xml.etree.ElementTree.Element("h1")
	header.text = "Index"
	hr = xml.etree.ElementTree.Element("hr")
	body.append(header)
	body.append(hr)
	index.append(body)
	for page in pages:
		a = xml.etree.ElementTree.Element("a", { "href": page.name })
		a.text = page.stem
		br = xml.etree.ElementTree.Element("br")
		body.append(a)
		body.append(br)
	return InternalPage(root.joinpath("./index.html"), xml.etree.ElementTree.tostring(index))

def build():
	root = pathlib.Path(__file__).resolve().parent

	output = root.joinpath("./docs")
	delete_path(output)
	output.mkdir(exist_ok=True)

	pages: list[pathlib.Path] = []

	for entry in root.iterdir():
		if entry.is_file():
			if entry.suffix == ".html":
				pages.append(entry)
			elif entry.suffix != ".py":
				with output.joinpath("./" + entry.name).open("wb") as out_stream:
					with entry.open("rb") as in_stream: out_stream.write(in_stream.read())

	pages.sort()
	pages.append(create_index(pages, root))

	for page in pages: process_page(page, output)

build()