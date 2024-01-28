### ASSET ALLOCATION - DATA LOADING MODULE

setwd("~/Documents/GitHub/asset-allocation")

# libraries ---------------------------------------------------------------

library(jsonlite)


# custom scripts ----------------------------------------------------------

source("./R/00_DataSourcing.R")

# in scope asset classes and markets --------------------------------------

asset_classes_config <- fromJSON("markets_mapping.JSON")


test <- yahoo_sourcing(asset_class_yahoo_subset = asset_classes_config[["Equities"]] %>% filter(data_source == "yahoo"),
                       output_dir = "~/Documents/asset-allocation-data")
sp <- sp_sourcing(asset_class_sp_subset = asset_classes_config[["Equities"]] %>% filter(data_source == "sp"),
                  output_dir = "/Users/andrei/Documents/asset-allocation-data")
