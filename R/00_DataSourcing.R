### ASSET ALLOCATION - DATA SOURCING MODULE (functions)

library(dplyr)
library(quantmod)
library(data.table)
library(futile.logger)
library(purrr)
library(tidyverse)
library(RSelenium)
library(netstat)
library(getPass)


# utility functions -------------------------------------------------------
stochasticWait <- function(mean_time, sd_time) {
  wait_time <- abs(rnorm(1, mean_time, sd_time))
  Sys.sleep(wait_time)
}

getMostRecentFile <- function(dir_path){
  # List all files in the folder
  files <- list.files(dir_path, full.names = TRUE)
  
  # Get the most recent file
  most_recent_file <- files[which.max(file.info(files)$mtime)]
  
  return(most_recent_file)
}

outputDataNaming <- function(market, index_id = NULL, data_source){
  output_name <- paste0(market, "_", data_source, "_export")
  return(output_name)
}

# sourcing functions ------------------------------------------------------
yahoo_sourcing <- function(asset_class_yahoo_subset, local_save = TRUE, data_saving_config){
  
  output_dir <- data_saving_config %>% filter(data_source == "yahoo") %>% pull(output_dir)
  output_dir <- paste0(output_dir, "/", Sys.Date())
  if(!dir.exists(output_dir)){
    dir.create(output_dir)
  }
  
  yahoo_data <- asset_class_yahoo_subset %>% pull(index_id_in_ds) %>% 
    lapply(FUN = function(symbol) getSymbols(Symbols = symbol, auto.assign = FALSE))
  
  
  custom_output <- function(data, market, index_name, symbol){
    
    if(local_save){
      file_name <- outputDataNaming(market, data_source = "yahoo")
      fwrite(x = data, file = paste0(output_dir, "/", file_name,"_",Sys.Date(), ".csv"))
      flog.info(paste0(index_name, " data (", market,") exported successfully!"), data %>% head(), capture = T)
      return(NULL)
    }else{
      return(data)
    }
    
  }
  
  OUTPUT <- list(data = yahoo_data, 
                 market = asset_class_yahoo_subset %>% pull(market),
                 index_name = asset_class_yahoo_subset %>% pull(index_name),
                 symbol = asset_class_yahoo_subset %>% pull(index_id_in_ds)) %>% 
    pwalk(custom_output)
  
  if(!local_save){
    return(OUTPUT)
  }else{
    return(NULL)
  }
  
}

sp_sourcing <- function(asset_class_sp_subset, data_saving_config, username = NULL, password = NULL){
  
  output_dir <- data_saving_config %>% filter(data_source == "sp") %>% pull(output_dir)
  output_dir <- paste0(output_dir, "/", Sys.Date())
  if(!dir.exists(output_dir)){
    dir.create(output_dir)
  }

  if(is.null(username)){
    username <- getPass("Enter email (S&P): ")
  }
  if(is.null(password)){
    password <- getPass("Enter password (S&P): ")
  }
  
  
  ### R selenium connection
  eCaps <- list(
    chromeOptions = 
      list(prefs = list(
        "profile.default_content_settings.popups" = 0L,
        "download.prompt_for_download" = FALSE,
        "download.default_directory" = output_dir
      )
      )
  )
  
  rs_driver_object <- rsDriver(
    browser = "chrome",
    chromever = "121.0.6167.85",
    verbose = FALSE,
    port = free_port(),
    extraCapabilities = eCaps
  )
  
  remDr <- rs_driver_object$client
  
  
  
  ### accessing Standard & Poor website
  remDr$navigate("https://www.spglobal.com/spdji/en/indices/equity/sp-asia-pacific-largemidcap/#overview")
  stochasticWait(2, 1)
  
  remDr$findElement(using = "id", value = "user-login")$clickElement()
  stochasticWait(5, 2)
  
  remDr$findElement(using = "id", value = "email")$sendKeysToElement(list(username))
  stochasticWait(4, 2)
  
  remDr$findElement(using = "id", value = "password")$sendKeysToElement(list(password))
  stochasticWait(2, 1)
  
  remDr$findElement(using = "id", value = "login-button")$clickElement()
  flog.info("S&P login completed!")
  stochasticWait(15, 2)
  
  
  
  ### finding download URL
  data_files <- remDr$findElements(using = 'xpath', "//div[@class='export  enableGateKeeping']/a")
  url <- sapply(data_files, function(element) element$getElementAttribute('href')) %>% unlist()
  
  if(is.null(url)){
    url <- "https://www.spglobal.com/spdji/en/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&redesignExport=true&languageId=1&selectedModule=PerformanceGraphView&selectedSubModule=Graph&yearFlag=tenYearFlag&indexId=348168"
  }else{
    url <- sub("yearFlag=[^&]+", "yearFlag=tenYearFlag", url) # setting the export time frame
  }
  
  
  
  ### downloading data (iterating over 'asset_class_sp_subset' rows)
  for (i in 1:nrow(asset_class_sp_subset)){
    
    index_id <- asset_class_sp_subset[i, "index_id_in_ds"]
    market <- asset_class_sp_subset[i, "market"]
    index_name <- asset_class_sp_subset[i, "index_name"]

    # replacing custom index_id inside url
    index_url <- sub(pattern = "indexId=[^&]+", replacement = paste0("indexId=",index_id), x = url)

    # download index data
    remDr$navigate(index_url)
    stochasticWait(10, 2)
    
    # rename downloaded file
    recent_file <- getMostRecentFile(output_dir)
    
    if (recent_file != paste0(output_dir, "/PerformanceGraphExport.xls")){
      stop("PerformanceGraphExport.xls is not the most recent file in output_dir!")
    }
    file_name <- outputDataNaming(market, index_id, data_source = "sp")
    file.rename(recent_file, paste0(output_dir, "/", file_name, "_", Sys.Date(),".xls"))
    
    flog.info(paste0(index_name, " data (", market,") exported successfully!"))
  }
  
  flog.info("All data from S&P extracted successfully")
  return(NULL)
}

dataSourcing <- function(assetClassConfig, data_saving_config, sp_username = NULL, sp_password = NULL){
  
  yahoo <- yahoo_sourcing(asset_class_yahoo_subset = assetClassConfig %>% filter(data_source == "yahoo"),
                          data_saving_config = data_saving_config)
  
  sp <- sp_sourcing(asset_class_sp_subset = assetClassConfig %>% filter(data_source == "sp"),
                    data_saving_config = data_saving_config,
                    username = sp_username,
                    password = sp_password)
  
  return(NULL)
}