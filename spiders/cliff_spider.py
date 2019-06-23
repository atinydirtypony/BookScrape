import scrapy
import re
import os


class CliffSpider(scrapy.Spider):
    name = "cliff"

    def start_requests(self):
        urls = [
            'https://www.cliffsnotes.com/literature?filter=ShowAll&sort=TITLE',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for book in response.css('li.note'):
            parent_folder_name = re.sub('[ &\'\.,:\(\)!]','_',book.css('div.note-name h4::text').get())
            follow_link = book.css('div.info a::attr(href)').get()
            if(not os.path.isdir('Results/'+parent_folder_name)):
                os.mkdir('Results/'+parent_folder_name)

            parser = self.book_page_parse_factory(parent_folder_name)
            yield scrapy.Request('https://www.cliffsnotes.com'+follow_link, parser)

    def book_page_parse_factory(self,parent_folder):
        def F(response):
            csv_index = ''
            for nav_link in response.css('section.secondary-navigation ul li a'):
                link_adress = nav_link.css('::attr(href)').get()
                page_name = nav_link.css('span::text').get()
                csv_index = csv_index + page_name+','+link_adress.split("/")[-1]+'\n'
                parser = self.chapter_page_parse_factory(parent_folder);
                yield scrapy.Request('https://www.cliffsnotes.com'+link_adress, parser)
            with open('Results/'+parent_folder+'/index.csv', 'wb') as csv:
                csv.write(csv_index.encode())
        return F

    def chapter_page_parse_factory(self,parent_folder):
        def F(response):
            page = response.url.split("/")[-1]
            filename = 'Results/'+parent_folder+'/'+page+'.html'
            print(filename)
            try:
                with open(filename, 'wb') as file:
                    file.write(response.body)
            except Exception as e:
                print(e)
