# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from scrapy.exceptions import DropItem


from kurdish_scrapy.settings import ALLOWED_LANGS, TEXT_MIN_WORD_COUNT


class LenPipeline:
    def process_item(self, item, spider):
        if item["word_count"] < TEXT_MIN_WORD_COUNT:
            print("Text is too short, dropping item")
            raise DropItem("Text is too short")

        return item


class LanguagePipeline:
    def process_item(self, item, spider):
        lang = item["lang"]
        if lang not in ALLOWED_LANGS:
            print(f"Dropping non-Kurdish text ({lang})")
            raise DropItem(f"Item is not Kurdish ({lang})")

        return item
