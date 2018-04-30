from django.db import models

class Search(models.Model):
    search_name = models.CharField(max_length=254)
    keyword = models.CharField(max_length=254)
    resultcount = models.CharField(max_length=10)
    searchdate = models.DateField()

    class Meta:
        db_table = 'connector_search'
        managed = True
        verbose_name = 'Search'
        verbose_name_plural = 'Searchs'

    def __str__(self):
        return self.searc_hname

class SearchResult(models.Model):
    searchid = models.IntegerField()
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    class Meta:
        db_table = 'connector_searchresult'
        managed = True
        verbose_name = 'SearchResult'
        verbose_name_plural = 'SearchResults'

    def __str__(self):
        return self.name
