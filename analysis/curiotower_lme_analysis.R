library(tidyverse)
library(lme4)
library(lmerTest)
#devtools::install_github("crsh/papaja")
library(papaja)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
dat = read_csv('curiotower_raw_data_run_0.csv')
glimpse(dat)

tower_stable_avg = dat %>% 
  filter(condition == 'stable') %>% 
  group_by(towerID) %>% 
  summarise(avg_stable_rating = mean(button_pressed))

dat_interesting = dat %>% select('button_pressed',
                     'num_blocks',
                     'stability',
                     'viewpoint',
                     'towerID',
                     'prolificID', 
                     'condition') %>% 
  filter(condition== 'interesting')
dat_interesting$stability = factor(dat_interesting$stability, order = TRUE, 
                       levels = c('low', 'med', 'high'))
dat_interesting$num_blocks_ordered = factor(dat_interesting$num_blocks, order = TRUE, 
                                levels = c('2', '4', '8'))


dat_full = merge(dat_interesting,tower_stable_avg,by=c("towerID"))





#LME interestingness_rating ~ Jitter + Height + (1 | tower) + (1 | subjID)
model0 = lmer(button_pressed ~ 
                (1|towerID)+
                (1|prolificID),data=dat_full)
summary(model0)

model1 = lmer(button_pressed ~ 1 + 
                num_blocks+
                (1|towerID)+
                (1|prolificID),data=dat_full)
summary(model1)

model2 = lmer(button_pressed ~ 1 + 
                num_blocks+
                stability + 
               (1|towerID)+
               (1|prolificID),data=dat_full)
summary(model2)

#copmare model1 and model 2
anova(model1,model2)


model3 = lmer(button_pressed ~ 1 + 
                stability * 
                num_blocks +
                (1|towerID)+
                (1|prolificID),data=dat_full)

apa_print(anova(model2,model3))



model4 = lmer(button_pressed ~ 1 + 
                stability *
                num_blocks +
                viewpoint+
                (1|towerID)+
                (1|prolificID),data=dat_full)
summary(model4)

model5 = lmer(button_pressed ~ 1 + 
                stability *
                num_blocks *
                viewpoint+
                (1|towerID)+
                (1|prolificID),data=dat_full)
summary(model5)

anova(model0, model1, model2, model3, model4, model5)

#Now add mean stability rating as first factor in best model
model6 = lmer(button_pressed ~ 1 + 
                stability * 
                num_blocks +
                avg_stable_rating+
                (1|towerID)+
                (1|prolificID),data=dat_full)
summary(model6)

anova(model3, model6)





