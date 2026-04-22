import markdown
from ebooklib import epub


class EPUBBuilder:
    def __init__(self, config):
        self.config = config

    def create_epub(self, md_content, output_path, title="Converted Magazine"):
        html = markdown.markdown(md_content, extensions=['extra', 'tables'])
        book = epub.EpubBook()
        book.set_identifier('id_jeff_project')
        book.set_title(title)
        book.set_language(self.config['output']['language'])
        book.add_author('Unknown')

        c1 = epub.EpubHtml(title='Content', file_name='content.xhtml', lang='en')
        c1.content = f"<html><body>{html}</body></html>"
        book.add_item(c1)

        if self.config['output']['add_toc']:
            book.toc = [epub.Link('content.xhtml', title, 'content')]

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', c1]

        epub.write_epub(output_path, book, {})
