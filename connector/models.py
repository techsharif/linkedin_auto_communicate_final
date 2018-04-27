from django.db import models

class Search(models.Model):
    searchid = models.ForeignKey('SearchResult', on_delete=models.CASCADE)
    searchname = models.CharField(max_length=254)
    keyword = models.CharField(max_length=254)
    resultcount = models.CharField(max_length=10)
    searchdate = models.DateField()

    def __str__(self):
        return self.searchname

class SearchResult(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'SearchResult'
        verbose_name_plural = 'SearchResults'

    def __str__(self):
        return self.name
