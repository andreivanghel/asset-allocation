

library(tidyverse)
library(RSelenium)
library(netstat)


#connection

rs_driver_object <- rsDriver(
  browser = "chrome",
  chromever = "121.0.6167.85",
  verbose = FALSE,
  port = free_port()
)

# access the client object
remDr <- rs_driver_object$client

remDr$open()

### access S&P website
remDr$navigate("https://www.spglobal.com/spdji/en/indices/equity/sp-asia-pacific-largemidcap/#overview")

### click login button
remDr$findElement(using = "id", value = "user-login")$clickElement()

### username & password
# Find the email and password fields by ID and fill them
remDr$findElement(using = "id", value = "email")$sendKeysToElement(list("andreivanghel@gmail.com"))
remDr$findElement(using = "id", value = "password")$sendKeysToElement(list("C8efb877*"))

### click login
remDr$findElement(using = "id", value = "login-button")$clickElement()


# Find the export button within the div by class name
data_files <- remDr$findElements(using = 'xpath', "//div[@class='export  enableGateKeeping']/a")

url <- sapply(data_files, function(element) element$getElementAttribute('href')) %>% unlist()
remDr$navigate(url)
remDr$navigate("https://www.spglobal.com/spdji/en/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&redesignExport=true&languageId=1&selectedModule=PerformanceGraphView&selectedSubModule=Graph&yearFlag=tenYearFlag&indexId=348168")

### customize -> yearFlag=tenYearFlag


### IN JSON FILE -> save:
# - index ID,
# - Index name...
# - URL (not necessarily needed...)

# https://www.spglobal.com/spdji/en/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&redesignExport=true&languageId=1&selectedModule=PerformanceGraphView&selectedSubModule=Graph&yearFlag=tenYearFlag&indexId=348170
# https://www.spglobal.com/spdji/en/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&redesignExport=true&languageId=1&selectedModule=PerformanceGraphView&selectedSubModule=Graph&yearFlag=oneYearFlag&indexId=348168
# https://www.spglobal.com/spdji/en/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&redesignExport=true&languageId=1&selectedModule=PerformanceGraphView&selectedSubModule=Graph&yearFlag=tenYearFlag&indexId=92395506


