library(tidyverse)
library(lme4)
library(lmerTest)
#devtools::install_github("crsh/papaja")
library(papaja)
library(MuMIn)

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
# Stability calculations-----------------------------
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
# Model building-----------------------------
'''


#LME interestingness_rating ~ Jitter + Height + (1 | tower) + (1 | subjID)
model0 = lmer(button_pressed ~ 1 + 
                jitter+
                (1|towerID)+
                (1|prolificID),data=df)
r.squaredGLMM(model0)

model1 = lmer(button_pressed ~ 1 + 
                num_blocks+
                (1|towerID)+
                (1|prolificID),data=df)
r.squaredGLMM(model1)

model2 = lmer(button_pressed ~ 1 + 
                num_blocks+
                jitter + 
               (1|towerID)+
               (1|prolificID),data=df)
r.squaredGLMM(model2)

model3 = lmer(button_pressed ~ 1 + 
                num_blocks * 
                jitter +
                (1|towerID)+
                (1|prolificID),data=df)

r.squaredGLMM(model3)

model4 = lmer(button_pressed ~ 1 + 
                num_blocks * 
                jitter +
                viewpoint+
                (1|towerID)+
                (1|prolificID),data=df)
r.squaredGLMM(model4)

anova(model1,model2,model3,model4)

model5 = lmer(button_pressed ~ 1 + 
                sd_hor+
                (1|towerID)+
                (1|prolificID),data=df)
summary(model5)
r.squaredGLMM(model5)

model6 = lmer(button_pressed ~ 1 + 
                forcemin+
                (1|towerID)+
                (1|prolificID),data=df)
summary(model6)
r.squaredGLMM(model6)

model7 = lmer(button_pressed ~ 1 + 
                color_offset+
                (1|towerID)+
                (1|prolificID),data=df)
summary(model7)
r.squaredGLMM(model7)


model8 = lmer(button_pressed ~ 1 + 
                num_blocks *
                sd_hor +
                (1|towerID)+
                (1|prolificID),data=df)
summary(model8)
r.squaredGLMM(model8)

model9 = lmer(button_pressed ~ 1 + 
                num_blocks * 
                sd_hor *
                forcemin+
                (1|towerID)+
                (1|prolificID),data=df)

summary(model9)
r.squaredGLMM(model9)

model10 = lmer(button_pressed ~ 1 + 
                num_blocks * 
                sd_hor *
                forcemin+
                avg_stable_rating+
                (1|towerID)+
                (1|prolificID),data=df)
r.squaredGLMM(model10)

model11 = lmer(button_pressed ~ 1 + 
                num_blocks * 
                sd_hor *
                forcemin+
                avg_stable_rating+
                color_offset+
                (1|towerID)+
                (1|prolificID),data=df)
r.squaredGLMM(model11)

anova(model8,model9,model10, model11)



