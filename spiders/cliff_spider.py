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
            print('Follow Link: '+follow_link)
            if(not os.path.isdir('Results/'+parent_folder_name)):
                print('Making folder: Results/'+parent_folder_name)
                os.mkdir('Results/'+parent_folder_name)

            parser = self.book_note_parse_factory(parent_folder_name)
            print(parser)
            response.follow(follow_link, parser)

    def book_note_parse_factory(self,parent_folder):
        def F(current_self, response):
            print(parent_folder)
            with open('Results/'+parent_folder+'/first_page.html', 'wb') as f:
                f.write(response.body)
        return F
