from tasks import process_path

result = process_path.delay('/public/dumps/public/enwiki/20211201/enwiki-20211201-pages-meta-history8.xml-p2535877p2535909.bz2')
print(result.get())
