### ASSET ALLOCATION - DATA LOADING MODULE


# libraries ---------------------------------------------------------------

library(dplyr)
library(quantmod)
library(jsonlite)


# in scope asset classes and markets --------------------------------------

asset_classes <- fromJSON("markets_mapping.JSON")
