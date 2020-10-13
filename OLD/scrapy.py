# ___________________________________________________
# Local application imports
# ___________________________________________________
from Apps.Scrapy.view import View

"""
creating the View() object and running it
"""
scrapy = View()
scrapy.configView()
scrapy.run()