library(lme4)
library(lmerTest)
library(caret)
library(tidyverse)
theme_set(theme_classic())
theme_update(# axis labels
  axis.title = element_text(size = 28),
  # tick labels
  axis.text = element_text(size = 24),
  # title 
  title = element_text(size = 24),
  legend.position = 'FALSE', 
  text = element_text(size=16), 
  element_line(size=1), 
  element_rect(size=2, color="#00000"))

primary_color = '#22AAAA'
secondary_color = '#252b31'
tertiary_color = '#c7cedf'
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

'''
Read in data from csv
'''
dat_raw = read_csv('curiotower_raw_data_run_0.csv')
glimpse(dat_raw)

tower_stable_avg = dat_raw %>% 
  filter(condition == 'stable') %>% 
  group_by(towerID) %>% 
  summarise(avg_stable_rating = mean(button_pressed))

dat_interesting = dat_raw %>% select('button_pressed',
                                 'num_blocks',
                                 'stability',
                                 'viewpoint',
                                 'towerID',
                                 'prolificID', 
                                 'condition') %>% 
  filter(condition== 'interesting')

dat_interesting$seed = as.numeric(str_sub(dat_interesting$towerID,-3,-3))
dat_interesting$stability = factor(dat_interesting$stability, order = TRUE, 
                                   levels = c('low', 'med', 'high'))
dat_interesting$jitter = dat_interesting$stability
dat_interesting$num_blocks_ordered = factor(dat_interesting$num_blocks, order = TRUE, 
                                            levels = c('2', '4', '8'))

dat_full = merge(dat_interesting,tower_stable_avg,by=c("towerID"))

'''
Merge with calculated values from poke test and other hdf5 
static measures like color, 2d silhouette, etc.
'''

df_stability_tests=read_csv('static-dynamic.csv')
df_stability_tests$sd_hor = df_stability_tests$sdmax
df_stability_tests$towerID= substr(df_stability_tests$towerID,
                                   1,
                                   nchar(df_stability_tests$towerID)-2)
glimpse(df_stability_tests)

dat_full$tower_id = substring(dat_full$towerID, 12,nchar(dat_full$towerID)-2)
#dat_full$tower_id = substr(dat_full$towerID,1,nchar(dat_full$towerID)-2)

dat_full = dat_full %>% 
  rename(
    tower_full_ID = towerID,
    towerID = tower_id
  )
glimpse(dat_full)
df = merge(dat_full,df_stability_tests,by=c("towerID"))

'''
Create a loop to test the model accuracy in predicting a holdout set from one seed
at a time. Store the R^2 values from each holdout set and take mean for each model
'''

get_r2 <- function(i, model){
  train_data = df %>% filter(seed != i)
  test_data = df %>% filter(seed == i)
  
  predictions <- model %>% predict(test_data)
  r2 = R2(predictions, test_data$button_pressed)
  return(r2)
}

get_mean_r2 <- function(model){
  r_sq_vals = c()
  for(i in 0:7){
    r_sq_vals = c(r_sq_vals, get_r2(i, model))
  }

  return(mean(r_sq_vals))
}

get_mean_r <- function(model){
  r_sq_vals = c()
  for(i in 0:7){
    r_sq_vals = c(r_sq_vals, get_r2(i, model))
  }
  
  return(mean(sqrt(r_sq_vals)))
}

get_model_r2<- function(model){
  return(summary(model)$r.squared)
}

#POSSIBLE MODELS
lm1 = lm(data = df, button_pressed ~ num_blocks)
#lm2 = lm(data = df, button_pressed ~ jitter)
lm2 = lm(data = df, button_pressed ~ jitter + num_blocks)
lm3 = lm(data = df, button_pressed ~ jitter * num_blocks)
lm4 = lm(data = df, button_pressed ~ jitter * num_blocks + viewpoint)
#lm6 = lm(data = df, button_pressed ~ sd_hor)
#lm5 = lm(data = df, button_pressed ~ num_blocks + sd_hor)
#lm6 = lm(data = df, button_pressed ~ num_blocks*sd_hor)
#lm7 = lm(data = df, button_pressed ~ forcemin)
#lm7 = lm(data = df, button_pressed ~ num_blocks*sd_hor +forcemin) 
lm5 = lm(data = df, button_pressed ~ color_offset)
lm8 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin)
lm = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin + color_offset)
lm9 = lm(data = df, button_pressed ~ avg_stable_rating)
lm10 = lm(data = df, button_pressed ~ num_blocks*sd_hor+avg_stable_rating)
lm11 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin+avg_stable_rating)
lm12 = lm(data = df, button_pressed ~ color_offset)
lm13 = lm(data = df, button_pressed ~ silhouette_height+silhouette_width+silhouette_jaggedness)
lm14 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin+avg_stable_rating+silhouette_height+silhouette_width+silhouette_jaggedness)
lm15 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin+avg_stable_rating+silhouette_height+silhouette_width+silhouette_jaggedness+ color_offset+color_diversity)
 


#MODELS USED IN COGSCI DRAFT 1
lm1 = lm(data = df, button_pressed ~ color_offset)
lm2 = lm(data = df, button_pressed ~ num_blocks)
lm3 = lm(data = df, button_pressed ~ jitter + num_blocks)
lm4 = lm(data = df, button_pressed ~ jitter * num_blocks)
lm5 = lm(data = df, button_pressed ~ jitter * num_blocks + viewpoint)
lm6 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin)
lm7 = lm(data = df, button_pressed ~ num_blocks*sd_hor*forcemin + color_offset)

model_names = c('1','2','3','4','5','6', '7')
#model_names = factor(model_names, c('1','2','3','4','5','6','7','8','9','10','11','12','13','14', '15'))

r2_vals = c(get_model_r2(lm1),
            get_model_r2(lm2),
            get_model_r2(lm3),
            get_model_r2(lm4),
            get_model_r2(lm5),
            get_model_r2(lm6),
            get_model_r2(lm7))
r2_vals

r2_out = data.frame(models = model_names, r2_vals = r2_vals)

ey <-  expression(R^2)
area.color <- c('Color', replicate(4,'Experimental'), replicate(2,'Computed'))
ggplot(data = r2_out) + 
  geom_bar(aes(x = model_names, y = r2_vals, fill = area.color), stat = 'identity')+
  scale_fill_manual(values=c(primary_color,secondary_color,tertiary_color))+
  ylab(ey)+
  xlab('Models')
                                                                                                                 "deepskyblue4"))
  

get_mean_r(lm12)


mean_r2s = c()
for(m in model_list){
  train_data = NULL
  test_data = NULL
  mean_r2s = c(mean_r2s,get_mean_r2(m))
}
mean_r2s

