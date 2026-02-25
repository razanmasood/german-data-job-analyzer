# NER Error Analysis Report

## Summary

- **Test samples**: 23
- **Gold entities**: 364
- **Predicted entities**: 458
- **Correct**: 216
- **Total errors**: 292

### Error Breakdown

| Category | Count | % of Errors |
|----------|------:|------------:|
| Missed entity (FN) | 48 | 16.4% |
| False alarm (FP) | 144 | 49.3% |
| Label confusion | 28 | 9.6% |
| Boundary error | 72 | 24.7% |

## Missed Entities (False Negatives)

Gold entities that the model failed to predict at all.

### 1. Sample 33

- **Gold**: `▁in ▁computer` (SKILL) [tokens 13:15]
- **Context**: ...▁or ▁PhD ) ▁in ▁computer ▁science , ▁robot...

### 2. Sample 33

- **Gold**: `▁applied` (SKILL) [tokens 35:36]
- **Context**: ...▁robot ics ▁or ▁applied ▁ ML ▁with...

### 3. Sample 33

- **Gold**: `▁with ▁production ▁de plo y` (SKILL) [tokens 38:43]
- **Context**: ...▁applied ▁ ML ▁with ▁production ▁de plo y ments ▁in ▁manipula...

### 4. Sample 33

- **Gold**: `,` (SKILL) [tokens 90:91]
- **Context**: ..., ▁D PO , ▁ RL HF...

### 5. Sample 33

- **Gold**: `,` (TOOL) [tokens 142:143]
- **Context**: .... g . , ▁ ROS ▁2...

### 6. Sample 146

- **Gold**: `,` (TOOL) [tokens 107:108]
- **Context**: ..., ▁RA G , ▁ ML /...

### 7. Sample 109

- **Gold**: `▁modern` (SKILL) [tokens 99:100]
- **Context**: ...▁good ▁knowledge ▁of ▁modern ▁ ML ▁framework...

### 8. Sample 17

- **Gold**: `▁and ▁Dev Op` (SKILL) [tokens 94:97]
- **Context**: ...▁as ▁code , ▁and ▁Dev Op s ▁best ▁practice...

### 9. Sample 86

- **Gold**: `▁mit ▁großen ▁Daten men` (SKILL) [tokens 133:137]
- **Context**: ...▁Erfahrungen ▁im ▁Umgang ▁mit ▁großen ▁Daten men gen ▁sowie ▁im...

### 10. Sample 77

- **Gold**: `▁of` (SKILL) [tokens 242:243]
- **Context**: ...▁product ive ▁operation ▁of ▁ ML /...

### 11. Sample 77

- **Gold**: `▁in ▁process ▁optimiza` (SKILL) [tokens 249:252]
- **Context**: ...Data ▁services ▁Experience ▁in ▁process ▁optimiza tion ▁ ,...

### 12. Sample 77

- **Gold**: `▁and ▁best ▁practice` (SKILL) [tokens 259:262]
- **Context**: ...▁standard ▁process es ▁and ▁best ▁practice s ▁Experience ▁in...

### 13. Sample 77

- **Gold**: `▁to ▁best ▁practice` (SKILL) [tokens 274:277]
- **Context**: ...▁efficient ▁code ▁according ▁to ▁best ▁practice s , ▁including...

### 14. Sample 77

- **Gold**: `▁including ▁unit` (SKILL) [tokens 279:281]
- **Context**: ...▁practice s , ▁including ▁unit ▁testing ▁and ▁de...

### 15. Sample 77

- **Gold**: `▁and ▁de bu` (SKILL) [tokens 282:285]
- **Context**: ...▁including ▁unit ▁testing ▁and ▁de bu gging ▁Experience ▁working...

### 16. Sample 37

- **Gold**: `▁im ▁struktur ierten ▁An forderung s` (SKILL) [tokens 113:119]
- **Context**: ...L ) ▁und ▁im ▁struktur ierten ▁An forderung s management ▁- ▁AI...

### 17. Sample 37

- **Gold**: `▁Bereich` (SKILL) [tokens 138:139]
- **Context**: ...enes ▁Studium ▁im ▁Bereich ▁Statistik , ▁Betriebs...

### 18. Sample 37

- **Gold**: `▁-` (TOOL) [tokens 159:160]
- **Context**: ...e ▁Qual ifikation ▁- ▁Re le vante...

### 19. Sample 69

- **Gold**: `▁-` (SKILL) [tokens 34:35]
- **Context**: ...▁skills ▁in ▁Python ▁- ▁ ML ▁framework...

### 20. Sample 69

- **Gold**: `▁Solid ▁software` (SKILL) [tokens 74:76]
- **Context**: ...s ▁) ▁- ▁Solid ▁software ▁engineering ▁and ▁data...

### 21. Sample 69

- **Gold**: `▁and ▁data ▁automat` (SKILL) [tokens 77:80]
- **Context**: ...▁Solid ▁software ▁engineering ▁and ▁data ▁automat ion ▁skills ▁-...

### 22. Sample 69

- **Gold**: `▁or` (TOOL) [tokens 100:101]
- **Context**: ...gging ▁Face , ▁or ▁ Stream lit...

### 23. Sample 79

- **Gold**: `▁for ▁algorithm` (SKILL) [tokens 18:20]
- **Context**: ...▁and ▁C ++ ▁for ▁algorithm ▁development ▁and ▁de...

### 24. Sample 79

- **Gold**: `▁and ▁de plo y` (SKILL) [tokens 21:25]
- **Context**: ...▁for ▁algorithm ▁development ▁and ▁de plo y ment . ▁2...

### 25. Sample 79

- **Gold**: `▁with` (SKILL) [tokens 69:70]
- **Context**: ...- on ▁experience ▁with ▁ phy sic...

### 26. Sample 65

- **Gold**: `▁in ▁front - end` (SKILL) [tokens 125:129]
- **Context**: ...▁required ▁and ▁experience ▁in ▁front - end ▁technologies ▁( HTML...

### 27. Sample 66

- **Gold**: `. ▁Projekt leitung skom pet` (SKILL) [tokens 66:71]
- **Context**: ...erfahrung ▁im ▁Consulting . ▁Projekt leitung skom pet enz : ▁Du...

### 28. Sample 133

- **Gold**: `,` (SKILL) [tokens 73:74]
- **Context**: ...▁ analytic s , ▁ ML /...

### 29. Sample 10

- **Gold**: `▁in ▁conduct ing` (SKILL) [tokens 13:16]
- **Context**: ...▁have ▁proven ▁experience ▁in ▁conduct ing ▁research , ▁abil...

### 30. Sample 10

- **Gold**: `▁to ▁develop` (SKILL) [tokens 25:27]
- **Context**: ...▁hands - on ▁to ▁develop ▁software , ▁anal...

### 31. Sample 10

- **Gold**: `, ▁anal y ze ▁computer` (SKILL) [tokens 28:33]
- **Context**: ...▁to ▁develop ▁software , ▁anal y ze ▁computer ▁systems , ▁strong...

### 32. Sample 10

- **Gold**: `▁and ▁work load ▁orchestr` (SKILL) [tokens 84:88]
- **Context**: ...▁performance ▁analysis , ▁and ▁work load ▁orchestr ation ▁Programm ing...

### 33. Sample 87

- **Gold**: `▁- ▁Laufe nde s` (SKILL) [tokens 2:6]
- **Context**: ...<s> ▁Profil ▁- ▁Laufe nde s ▁Studium ▁z ....

### 34. Sample 87

- **Gold**: `▁- ▁Pflicht praktik` (SKILL) [tokens 26:29]
- **Context**: ...▁gerne ▁Data ▁Science ▁- ▁Pflicht praktik um ▁mit ▁Dauer...

### 35. Sample 87

- **Gold**: `, ▁technische s` (SKILL) [tokens 45:48]
- **Context**: ...e ▁Arbeits weise , ▁technische s ▁Verständnis ▁- ▁sehr...

### 36. Sample 83

- **Gold**: `,` (TOOL) [tokens 82:83]
- **Context**: ..., ▁Open MP , ▁ MPI ,...

### 37. Sample 83

- **Gold**: `▁doing ▁low - level ▁performance ▁optimiza` (SKILL) [tokens 97:103]
- **Context**: ...s ▁on ▁experience ▁doing ▁low - level ▁performance ▁optimiza tions . ▁In...

### 38. Sample 28

- **Gold**: `▁als ▁IT - Consult` (SKILL) [tokens 45:49]
- **Context**: .... B . ▁als ▁IT - Consult ant , ▁Software...

### 39. Sample 28

- **Gold**: `▁als ▁IT - Consult` (SKILL) [tokens 107:111]
- **Context**: .... B . ▁als ▁IT - Consult ant , ▁Software...

### 40. Sample 28

- **Gold**: `, ▁Data ▁S cient` (SKILL) [tokens 116:120]
- **Context**: ...▁Software ▁Engine er , ▁Data ▁S cient ist ). ▁Vers...

### 41. Sample 16

- **Gold**: `▁of` (SKILL) [tokens 46:47]
- **Context**: ...▁Strong ▁gras p ▁of ▁ QA ▁...

### 42. Sample 16

- **Gold**: `▁and ▁modern ▁testing ▁method ologie` (SKILL) [tokens 51:56]
- **Context**: ...QA ▁ architecture ▁and ▁modern ▁testing ▁method ologie s . ▁Deep...

### 43. Sample 16

- **Gold**: `, ▁Frau d ▁det` (SKILL) [tokens 237:241]
- **Context**: ...▁Audi ence ▁Data , ▁Frau d ▁det ection ). </s>...

### 44. Sample 144

- **Gold**: `▁in ▁data` (SKILL) [tokens 26:28]
- **Context**: ...▁years ▁of ▁experience ▁in ▁data ▁science ▁and /...

### 45. Sample 144

- **Gold**: `or ▁data` (SKILL) [tokens 31:33]
- **Context**: ...▁science ▁and / or ▁data ▁engineering ▁role s...

### 46. Sample 144

- **Gold**: `,` (SKILL) [tokens 132:133]
- **Context**: ...▁Trans former s , ▁ RL HF...

### 47. Sample 144

- **Gold**: `,` (SKILL) [tokens 203:204]
- **Context**: ...t ▁chain s , ▁ embe dding...

### 48. Sample 144

- **Gold**: `▁or ▁visual` (SKILL) [tokens 256:258]
- **Context**: ...▁ analytic s ▁or ▁visual ization ▁tools ▁(...

## False Alarms (False Positives)

Predicted entities that do not overlap with any gold entity.

### 1. Sample 33

- **Pred**: `al` (SKILL) [tokens 21:22]
- **Context**: ...ics , ▁electric al ▁engineering , ▁or...

### 2. Sample 33

- **Pred**: `▁or` (SKILL) [tokens 34:35]
- **Context**: ...▁in ▁robot ics ▁or ▁applied ▁ ML...

### 3. Sample 33

- **Pred**: `▁in ▁manipula` (SKILL) [tokens 44:46]
- **Context**: ...plo y ments ▁in ▁manipula tion ▁or ▁mobile...

### 4. Sample 33

- **Pred**: `▁robot` (SKILL) [tokens 49:50]
- **Context**: ...tion ▁or ▁mobile ▁robot ics . ▁Deep...

### 5. Sample 33

- **Pred**: `▁and ▁vision - language - action` (SKILL) [tokens 66:72]
- **Context**: ..., ▁reason ing ▁and ▁vision - language - action ▁models , ▁dif...

### 6. Sample 33

- **Pred**: `▁(` (TOOL) [tokens 84:85]
- **Context**: ...tu ning ▁methods ▁( PE FT ,...

### 7. Sample 33

- **Pred**: `,` (TOOL) [tokens 87:88]
- **Context**: ...▁( PE FT , ▁D PO ,...

### 8. Sample 33

- **Pred**: `RL` (TOOL) [tokens 92:93]
- **Context**: ...PO , ▁ RL HF ). ▁Strong...

### 9. Sample 33

- **Pred**: `▁with ▁deep ▁learning` (SKILL) [tokens 106:109]
- **Context**: ...++ ▁and ▁experience ▁with ▁deep ▁learning ▁framework s ▁(...

### 10. Sample 146

- **Pred**: `▁` (SKILL) [tokens 61:62]
- **Context**: ...▁Data ▁Science , ▁ ML - ▁oder...

### 11. Sample 146

- **Pred**: `▁für` (SKILL) [tokens 70:71]
- **Context**: ...Um feld ▁Leidenschaft ▁für ▁Daten , ▁AI...

### 12. Sample 146

- **Pred**: `▁RA` (SKILL) [tokens 105:106]
- **Context**: ...ze ssen , ▁RA G , ▁...

### 13. Sample 146

- **Pred**: `▁ ML` (SKILL) [tokens 108:110]
- **Context**: ...▁RA G , ▁ ML / DL ,...

### 14. Sample 146

- **Pred**: `▁L LM` (SKILL) [tokens 113:115]
- **Context**: .../ DL , ▁L LM s , ▁Panda...

### 15. Sample 109

- **Pred**: `▁and ▁production ▁de plo y` (SKILL) [tokens 40:45]
- **Context**: ...▁in ▁the ▁design ▁and ▁production ▁de plo y ment ▁of ▁N...

### 16. Sample 109

- **Pred**: `es ▁Evalua tion ▁methods` (SKILL) [tokens 87:91]
- **Context**: ...- based ▁approach es ▁Evalua tion ▁methods ▁for ▁Gen AI...

### 17. Sample 109

- **Pred**: `▁ architecture` (SKILL) [tokens 148:150]
- **Context**: ...▁cloud - based ▁ architecture s ▁and ▁M...

### 18. Sample 109

- **Pred**: `▁/ ▁de plo y ment ▁work flow` (SKILL) [tokens 155:162]
- **Context**: ...▁M LO ps ▁/ ▁de plo y ment ▁work flow s ▁on ▁platform...

### 19. Sample 17

- **Pred**: `, ▁computer` (SKILL) [tokens 10:12]
- **Context**: ...▁of ▁information ▁technology , ▁computer ▁science ▁or ▁comparable...

### 20. Sample 17

- **Pred**: `▁ architecture s ▁and ▁tool` (SKILL) [tokens 55:60]
- **Context**: ...▁Mono re po ▁ architecture s ▁and ▁tool ing ▁( Tur...

### 21. Sample 147

- **Pred**: `▁( Business` (SKILL) [tokens 7:9]
- **Context**: ...▁A ▁completed ▁degree ▁( Business ▁Administration , ▁Business...

### 22. Sample 147

- **Pred**: `, ▁Business ▁Informati` (SKILL) [tokens 10:13]
- **Context**: ...▁( Business ▁Administration , ▁Business ▁Informati cs , ▁Data...

### 23. Sample 147

- **Pred**: `, ▁Data` (SKILL) [tokens 14:16]
- **Context**: ...▁Business ▁Informati cs , ▁Data ▁Science , ▁etc...

### 24. Sample 147

- **Pred**: `▁and ▁agenti c ▁concept` (SKILL) [tokens 68:72]
- **Context**: ...TL ▁pipe lines ▁and ▁agenti c ▁concept s ▁are ▁not...

### 25. Sample 86

- **Pred**: `richtung` (SKILL) [tokens 17:18]
- **Context**: ...▁in ▁der ▁Fach richtung ▁Informati k ,...

### 26. Sample 86

- **Pred**: `, ▁Wirtschafts informati` (SKILL) [tokens 20:23]
- **Context**: ...richtung ▁Informati k , ▁Wirtschafts informati k ▁oder ▁ein...

### 27. Sample 86

- **Pred**: `▁ ML - Model` (SKILL) [tokens 71:75]
- **Context**: ...▁und ▁Pflege ▁von ▁ ML - Model len ▁in ▁der...

### 28. Sample 86

- **Pred**: `▁( Ter ra` (TOOL) [tokens 146:149]
- **Context**: ...structure ▁as ▁Code ▁( Ter ra form , ▁ARM...

### 29. Sample 86

- **Pred**: `,` (TOOL) [tokens 150:151]
- **Context**: ...Ter ra form , ▁ARM ). ▁Team...

### 30. Sample 77

- **Pred**: `▁& ▁database` (SKILL) [tokens 120:122]
- **Context**: ...▁knowledge ▁of ▁SQL ▁& ▁database s ▁and ▁experience...

### 31. Sample 77

- **Pred**: `able` (SKILL) [tokens 229:230]
- **Context**: ...▁efficient ▁and ▁scal able ▁Big ▁Data ▁and...

### 32. Sample 37

- **Pred**: `pot hes entes` (SKILL) [tokens 16:19]
- **Context**: ...▁Verfahren ▁( Hy pot hes entes ts , ▁Sign...

### 33. Sample 37

- **Pred**: `▁und` (TOOL) [tokens 40:41]
- **Context**: ...▁mit ▁Datenbank systemen ▁und ▁SQL ▁- ▁Kenntnis...

### 34. Sample 37

- **Pred**: `▁oder` (TOOL) [tokens 77:78]
- **Context**: ...B . ▁Python ▁oder ▁R ▁- ▁Erfahrung...

### 35. Sample 37

- **Pred**: `▁der ▁method ischen ▁Daten auf bereit` (SKILL) [tokens 101:107]
- **Context**: ...▁- ▁Erfahrung ▁in ▁der ▁method ischen ▁Daten auf bereit ung ▁( ET...

### 36. Sample 37

- **Pred**: `▁- ▁AI -` (SKILL) [tokens 120:123]
- **Context**: ...forderung s management ▁- ▁AI - Er fa hrung...

### 37. Sample 37

- **Pred**: `▁Bereichen ▁Daten` (SKILL) [tokens 166:168]
- **Context**: ...▁Erfahrung ▁in ▁den ▁Bereichen ▁Daten analyse ▁oder ▁Business...

### 38. Sample 37

- **Pred**: `▁oder ▁Business` (SKILL) [tokens 169:171]
- **Context**: ...▁Bereichen ▁Daten analyse ▁oder ▁Business ▁Intelligence ▁- ▁Sicher...

### 39. Sample 69

- **Pred**: `,` (SKILL) [tokens 20:21]
- **Context**: ...▁Master ▁( CS , ▁Physic s ,...

### 40. Sample 69

- **Pred**: `,` (SKILL) [tokens 23:24]
- **Context**: ..., ▁Physic s , ▁Math , ▁or...

### 41. Sample 69

- **Pred**: `▁and ▁API` (SKILL) [tokens 56:58]
- **Context**: ...F low ▁) ▁and ▁API s ▁( ▁Post...

### 42. Sample 69

- **Pred**: `▁R` (SKILL) [tokens 68:69]
- **Context**: ...▁Sup a base ▁R EST ▁API s...

### 43. Sample 69

- **Pred**: `EST ▁API` (TOOL) [tokens 69:71]
- **Context**: ...a base ▁R EST ▁API s ▁) ▁-...

### 44. Sample 79

- **Pred**: `▁to ▁robot` (SKILL) [tokens 53:55]
- **Context**: ...ment ▁learning ▁applied ▁to ▁robot ics ▁or ▁similar...

### 45. Sample 79

- **Pred**: `▁modern ▁control` (SKILL) [tokens 121:123]
- **Context**: ...▁classic al ▁and ▁modern ▁control ▁theory , ▁loco...

### 46. Sample 79

- **Pred**: `source` (SKILL) [tokens 145:146]
- **Context**: ...▁to ▁open - source ▁ ML ▁or...

### 47. Sample 79

- **Pred**: `▁` (SKILL) [tokens 146:147]
- **Context**: ...▁open - source ▁ ML ▁or ▁robot...

### 48. Sample 79

- **Pred**: `▁in` (SKILL) [tokens 162:163]
- **Context**: .... D . ▁in ▁Robot ics ,...

### 49. Sample 79

- **Pred**: `,` (SKILL) [tokens 165:166]
- **Context**: ...▁in ▁Robot ics , ▁Computer ▁Science ,...

### 50. Sample 79

- **Pred**: `,` (SKILL) [tokens 168:169]
- **Context**: ..., ▁Computer ▁Science , ▁Mechanic al ▁Engineering...

### 51. Sample 79

- **Pred**: `al` (SKILL) [tokens 170:171]
- **Context**: ...▁Science , ▁Mechanic al ▁Engineering , ▁or...

### 52. Sample 65

- **Pred**: `▁in ▁late - s` (SKILL) [tokens 67:71]
- **Context**: ...▁scientific ▁domain ▁knowledge ▁in ▁late - s tage ▁ pharma...

### 53. Sample 65

- **Pred**: `u tical` (SKILL) [tokens 75:77]
- **Context**: ...▁ pharma ce u tical ▁development , ▁including...

### 54. Sample 65

- **Pred**: `▁including ▁Medical` (SKILL) [tokens 79:81]
- **Context**: ...tical ▁development , ▁including ▁Medical ▁Affairs , ▁Clinic...

### 55. Sample 65

- **Pred**: `, ▁Clinic al` (SKILL) [tokens 82:85]
- **Context**: ...▁including ▁Medical ▁Affairs , ▁Clinic al ▁Development , ▁Pharma...

### 56. Sample 65

- **Pred**: `, ▁Pharma co vigil` (SKILL) [tokens 86:90]
- **Context**: ...▁Clinic al ▁Development , ▁Pharma co vigil ance , ▁Health...

### 57. Sample 65

- **Pred**: `, ▁Health ▁Economic s ▁& ▁Out com es` (SKILL) [tokens 91:99]
- **Context**: ...co vigil ance , ▁Health ▁Economic s ▁& ▁Out com es ▁Research ▁( HE...

### 58. Sample 65

- **Pred**: `▁( HE` (SKILL) [tokens 100:102]
- **Context**: ...com es ▁Research ▁( HE OR ), ▁or...

### 59. Sample 65

- **Pred**: `▁or` (SKILL) [tokens 104:105]
- **Context**: ...HE OR ), ▁or ▁Epidemi ology ,...

### 60. Sample 65

- **Pred**: `Uni x -` (SKILL) [tokens 149:152]
- **Context**: ...▁with ▁Linux / Uni x - based ▁OS ▁or...

### 61. Sample 65

- **Pred**: `based` (TOOL) [tokens 152:153]
- **Context**: ...Uni x - based ▁OS ▁or ▁Do...

### 62. Sample 65

- **Pred**: `▁of` (SKILL) [tokens 179:180]
- **Context**: ...▁as ▁basic ▁understanding ▁of ▁agents ▁and ▁agenti...

### 63. Sample 65

- **Pred**: `▁and ▁agenti c ▁work flow` (SKILL) [tokens 181:186]
- **Context**: ...▁understanding ▁of ▁agents ▁and ▁agenti c ▁work flow s ▁( M...

### 64. Sample 65

- **Pred**: `▁with ▁drug ▁pipe` (SKILL) [tokens 214:217]
- **Context**: ...ly ▁also ▁experience ▁with ▁drug ▁pipe line ▁or ▁trial...

### 65. Sample 65

- **Pred**: `▁or ▁trial ▁CI ▁database` (SKILL) [tokens 218:222]
- **Context**: ...▁drug ▁pipe line ▁or ▁trial ▁CI ▁database s ▁( e...

### 66. Sample 65

- **Pred**: `. ▁Clari` (TOOL) [tokens 227:229]
- **Context**: ...e . g . ▁Clari vate ’ s...

### 67. Sample 65

- **Pred**: `s ▁Corte` (TOOL) [tokens 231:233]
- **Context**: ...▁Clari vate ’ s ▁Corte llis ▁Competi tive...

### 68. Sample 65

- **Pred**: `llis ▁Competi tive` (SKILL) [tokens 233:236]
- **Context**: ...’ s ▁Corte llis ▁Competi tive ▁Intelligence , ▁Cit...

### 69. Sample 65

- **Pred**: `, ▁Cit` (TOOL) [tokens 237:239]
- **Context**: ...▁Competi tive ▁Intelligence , ▁Cit eline ’ s...

### 70. Sample 65

- **Pred**: `s ▁Tri altro` (TOOL) [tokens 241:244]
- **Context**: ...▁Cit eline ’ s ▁Tri altro ve ▁or ▁Pharma...

### 71. Sample 65

- **Pred**: `▁or` (SKILL) [tokens 245:246]
- **Context**: ...▁Tri altro ve ▁or ▁Pharma project s...

### 72. Sample 65

- **Pred**: `▁Pharma project` (TOOL) [tokens 246:248]
- **Context**: ...altro ve ▁or ▁Pharma project s ). ▁-...

### 73. Sample 65

- **Pred**: `▁using ▁relation al ▁database` (SKILL) [tokens 296:300]
- **Context**: ...▁data . ▁Experience ▁using ▁relation al ▁database s ▁and ▁SQL...

### 74. Sample 132

- **Pred**: `▁a ▁Machine` (SKILL) [tokens 7:9]
- **Context**: ...ll ▁Do ▁As ▁a ▁Machine ▁Learning ▁Engine er...

### 75. Sample 132

- **Pred**: `▁new` (SKILL) [tokens 82:83]
- **Context**: ...▁Design ▁and ▁build ▁new ▁ ML ▁and...

### 76. Sample 132

- **Pred**: `▁` (SKILL) [tokens 83:84]
- **Context**: ...▁and ▁build ▁new ▁ ML ▁and ▁data...

### 77. Sample 132

- **Pred**: `▁existing` (SKILL) [tokens 95:96]
- **Context**: ...▁as ▁optim izing ▁existing ▁ ML ▁and...

### 78. Sample 132

- **Pred**: `▁` (SKILL) [tokens 96:97]
- **Context**: ...▁optim izing ▁existing ▁ ML ▁and ▁data...

### 79. Sample 132

- **Pred**: `▁and` (SKILL) [tokens 246:247]
- **Context**: ...▁of ▁back end ▁and ▁ ML ▁experience...

### 80. Sample 132

- **Pred**: `▁` (SKILL) [tokens 247:248]
- **Context**: ...▁back end ▁and ▁ ML ▁experience :...

### 81. Sample 132

- **Pred**: `, ▁distribu ted ▁process ing ▁pipe` (SKILL) [tokens 282:288]
- **Context**: ...▁experience ▁with ▁Python , ▁distribu ted ▁process ing ▁pipe lines ▁( H...

### 82. Sample 132

- **Pred**: `▁data set` (SKILL) [tokens 305:307]
- **Context**: ...▁and ▁very ▁large ▁data set s ▁– ▁statistic...

### 83. Sample 132

- **Pred**: `▁–` (SKILL) [tokens 308:309]
- **Context**: ...▁data set s ▁– ▁statistic al ▁analysis...

### 84. Sample 132

- **Pred**: `.` (SKILL) [tokens 320:321]
- **Context**: ...▁optim izing ▁storage . ▁Cloud ▁profi cie...

### 85. Sample 132

- **Pred**: `▁with` (SKILL) [tokens 330:331]
- **Context**: ...tensi ve ▁experience ▁with ▁cloud ▁and ▁infrastructure...

### 86. Sample 132

- **Pred**: `▁and ▁infrastructure` (SKILL) [tokens 332:334]
- **Context**: ...▁experience ▁with ▁cloud ▁and ▁infrastructure ▁services , ▁including...

### 87. Sample 132

- **Pred**: `▁as` (SKILL) [tokens 340:341]
- **Context**: ..., ▁as ▁well ▁as ▁de plo ying...

### 88. Sample 132

- **Pred**: `▁in ▁cloud ▁environment` (SKILL) [tokens 348:351]
- **Context**: ...▁man aging ▁infrastructure ▁in ▁cloud ▁environment s . ▁Operation...

### 89. Sample 132

- **Pred**: `▁for ▁clean` (SKILL) [tokens 374:376]
- **Context**: .... ▁Strong ▁passion ▁for ▁clean ▁code ▁and ▁robust...

### 90. Sample 132

- **Pred**: `▁and` (SKILL) [tokens 377:378]
- **Context**: ...▁for ▁clean ▁code ▁and ▁robust ▁ architecture...

### 91. Sample 132

- **Pred**: `▁` (SKILL) [tokens 379:380]
- **Context**: ...▁code ▁and ▁robust ▁ architecture , ▁with...

### 92. Sample 66

- **Pred**: `▁für` (SKILL) [tokens 8:9]
- **Context**: ...▁Be geist erung ▁für ▁Daten : ▁Mit...

### 93. Sample 133

- **Pred**: `▁strong ▁data` (SKILL) [tokens 36:38]
- **Context**: .... ) ▁with ▁strong ▁data ▁science ▁experience ▁Or...

### 94. Sample 133

- **Pred**: `▁in ▁Computer` (SKILL) [tokens 46:48]
- **Context**: ...' s ▁degree ▁in ▁Computer ▁Science , ▁Data...

### 95. Sample 133

- **Pred**: `▁in` (SKILL) [tokens 68:69]
- **Context**: ...▁years ' ▁experience ▁in ▁data ▁ analytic...

### 96. Sample 133

- **Pred**: `▁ analytic` (SKILL) [tokens 70:72]
- **Context**: ...▁experience ▁in ▁data ▁ analytic s , ▁...

### 97. Sample 70

- **Pred**: `holder` (SKILL) [tokens 50:51]
- **Context**: ...- sta ke holder ▁ ML /...

### 98. Sample 70

- **Pred**: `▁` (SKILL) [tokens 51:52]
- **Context**: ...sta ke holder ▁ ML / data...

### 99. Sample 70

- **Pred**: `▁production ▁Deep ▁` (SKILL) [tokens 61:64]
- **Context**: ...▁from ▁concept ▁to ▁production ▁Deep ▁ ML ▁and ▁cloud...

### 100. Sample 70

- **Pred**: `▁and ▁cloud` (SKILL) [tokens 65:67]
- **Context**: ...▁Deep ▁ ML ▁and ▁cloud ▁expertise ▁including ▁hands...

### 101. Sample 70

- **Pred**: `▁practice` (SKILL) [tokens 82:83]
- **Context**: ...▁M LO ps ▁practice s , ▁and...

### 102. Sample 70

- **Pred**: `▁services` (SKILL) [tokens 89:90]
- **Context**: ...▁A WS ▁cloud ▁services ▁Production ▁ ML...

### 103. Sample 70

- **Pred**: `▁ ML ▁de plo y` (SKILL) [tokens 91:96]
- **Context**: ...▁cloud ▁services ▁Production ▁ ML ▁de plo y ment ▁experience ▁with...

### 104. Sample 70

- **Pred**: `▁ ML` (SKILL) [tokens 115:117]
- **Context**: ...- s cale ▁ ML ▁systems ▁in ▁production...

### 105. Sample 10

- **Pred**: `.` (SKILL) [tokens 66:67]
- **Context**: ..., ▁Gen ▁AI . ▁Systems ▁experience :...

### 106. Sample 87

- **Pred**: `▁eines ▁M INT - F ach` (SKILL) [tokens 11:17]
- **Context**: .... B . ▁eines ▁M INT - F ach s ▁oder ▁Sport...

### 107. Sample 87

- **Pred**: `▁oder ▁Sport wissenschaft` (SKILL) [tokens 18:21]
- **Context**: ...F ach s ▁oder ▁Sport wissenschaft en , ▁gerne...

### 108. Sample 57

- **Pred**: `▁( Ma chine` (SKILL) [tokens 34:37]
- **Context**: ...elles ▁Lern en ▁( Ma chine ▁Learning ), ▁Statist...

### 109. Sample 57

- **Pred**: `▁in` (SKILL) [tokens 53:54]
- **Context**: ...▁Sehr ▁gute ▁Erfahrungen ▁in ▁klassische n ▁und...

### 110. Sample 57

- **Pred**: `▁ag` (SKILL) [tokens 57:58]
- **Context**: ...▁klassische n ▁und ▁ag ilen ▁Kooperation s...

### 111. Sample 57

- **Pred**: `▁Kooperation s form` (SKILL) [tokens 59:62]
- **Context**: ...▁und ▁ag ilen ▁Kooperation s form en ▁Her vor...

### 112. Sample 57

- **Pred**: `▁von` (SKILL) [tokens 71:72]
- **Context**: ...▁in ▁der ▁Leitung ▁von ▁strategi sch ▁aus...

### 113. Sample 57

- **Pred**: `sch ▁aus gerichte` (SKILL) [tokens 73:76]
- **Context**: ...▁Leitung ▁von ▁strategi sch ▁aus gerichte ten ▁Projekt en...

### 114. Sample 57

- **Pred**: `▁von ▁AI ▁Use ▁Case` (SKILL) [tokens 86:90]
- **Context**: ...▁in ▁der ▁Umsetzung ▁von ▁AI ▁Use ▁Case s ▁Sehr ▁gutes...

### 115. Sample 57

- **Pred**: `▁der ▁statisti schen` (SKILL) [tokens 102:105]
- **Context**: ...▁umfangreiche ▁Erfahrung ▁in ▁der ▁statisti schen ▁Analyse ▁und ▁statisti...

### 116. Sample 57

- **Pred**: `▁und ▁statisti schen ▁Mess` (SKILL) [tokens 106:110]
- **Context**: ...▁statisti schen ▁Analyse ▁und ▁statisti schen ▁Mess ungen ▁Her vor...

### 117. Sample 57

- **Pred**: `▁der ▁log ischen ▁Daten modell` (SKILL) [tokens 118:123]
- **Context**: ...▁Kenntnis se ▁in ▁der ▁log ischen ▁Daten modell ierung ▁Her vor...

### 118. Sample 57

- **Pred**: `en ▁Big ▁Data ▁Architektur` (SKILL) [tokens 132:136]
- **Context**: ...se ▁in ▁komplex en ▁Big ▁Data ▁Architektur en ▁Sehr ▁gute...

### 119. Sample 83

- **Pred**: `▁in ▁Computer` (SKILL) [tokens 4:6]
- **Context**: ...▁An ▁advanced ▁degree ▁in ▁Computer ▁Science , ▁Computer...

### 120. Sample 83

- **Pred**: `, ▁Computer` (SKILL) [tokens 7:9]
- **Context**: ...▁in ▁Computer ▁Science , ▁Computer ▁Engineering , ▁or...

### 121. Sample 83

- **Pred**: `▁with` (SKILL) [tokens 109:110]
- **Context**: ...- depth ▁expertise ▁with ▁CPU ▁and ▁GPU...

### 122. Sample 83

- **Pred**: `▁in ▁parallel` (SKILL) [tokens 145:147]
- **Context**: .... ▁Expert ise ▁in ▁parallel ization ▁and ▁performance...

### 123. Sample 105

- **Pred**: `▁und ▁Web plattform` (SKILL) [tokens 29:32]
- **Context**: ..., ▁System en ▁und ▁Web plattform en ▁für ▁verschieden...

### 124. Sample 105

- **Pred**: `▁von ▁Cloud - In fra` (SKILL) [tokens 51:56]
- **Context**: ...▁und ▁Optim ierung ▁von ▁Cloud - In fra struktur en ▁und...

### 125. Sample 105

- **Pred**: `▁und ▁Machine` (SKILL) [tokens 77:79]
- **Context**: ...▁Intel ligen z ▁und ▁Machine ▁Learning ▁: ▁Entwicklung...

### 126. Sample 105

- **Pred**: `▁und ▁Data` (SKILL) [tokens 131:133]
- **Context**: .... ▁Big ▁Data ▁und ▁Data ▁Science ▁: ▁Nutzung...

### 127. Sample 105

- **Pred**: `▁von ▁Daten` (SKILL) [tokens 136:138]
- **Context**: ...▁Science ▁: ▁Nutzung ▁von ▁Daten analyse , ▁Datenbank...

### 128. Sample 105

- **Pred**: `, ▁Datenbank` (SKILL) [tokens 139:141]
- **Context**: ...▁von ▁Daten analyse , ▁Datenbank en ▁und ▁modern...

### 129. Sample 105

- **Pred**: `▁Software` (SKILL) [tokens 222:223]
- **Context**: .... ▁A gile ▁Software entwicklung ▁: ▁Anwendung...

### 130. Sample 105

- **Pred**: `.` (SKILL) [tokens 271:272]
- **Context**: ...z . B . ▁Informati k ,...

### 131. Sample 105

- **Pred**: `, ▁Software` (SKILL) [tokens 274:276]
- **Context**: .... ▁Informati k , ▁Software ▁Engineering , ▁Wirtschafts...

### 132. Sample 105

- **Pred**: `, ▁Wirtschafts informati` (SKILL) [tokens 277:280]
- **Context**: ..., ▁Software ▁Engineering , ▁Wirtschafts informati k ). ▁Be...

### 133. Sample 16

- **Pred**: `▁` (SKILL) [tokens 17:18]
- **Context**: ...▁in ▁software ▁quality ▁ assurance ▁or ▁engineering...

### 134. Sample 16

- **Pred**: `▁&` (SKILL) [tokens 90:91]
- **Context**: ...park . ▁Cloud ▁& ▁Database ▁Profi cie...

### 135. Sample 16

- **Pred**: `)` (SKILL) [tokens 118:119]
- **Context**: ...▁Mon go DB ) ▁database s ▁to...

### 136. Sample 16

- **Pred**: `/` (SKILL) [tokens 169:170]
- **Context**: ...▁have : ▁AI / ML ▁Litera cy...

### 137. Sample 144

- **Pred**: `,` (SKILL) [tokens 13:14]
- **Context**: ..., ▁data ▁engineering , ▁ma thema tics...

### 138. Sample 144

- **Pred**: `▁( Gen )` (SKILL) [tokens 38:41]
- **Context**: ...s , ▁including ▁( Gen ) AI - related...

### 139. Sample 144

- **Pred**: `▁with ▁big - data` (SKILL) [tokens 48:52]
- **Context**: ...▁Profi cie ncy ▁with ▁big - data ▁tools ▁( e...

### 140. Sample 144

- **Pred**: `▁in` (SKILL) [tokens 73:74]
- **Context**: ...s ▁Strong ▁experience ▁in ▁ ML ▁Model...

### 141. Sample 144

- **Pred**: `▁ ML ▁Model` (SKILL) [tokens 74:77]
- **Context**: ...▁Strong ▁experience ▁in ▁ ML ▁Model s ▁with ▁correspond...

### 142. Sample 144

- **Pred**: `,` (TOOL) [tokens 136:137]
- **Context**: ...▁ RL HF , ▁fine - tu...

### 143. Sample 144

- **Pred**: `▁visual` (SKILL) [tokens 164:165]
- **Context**: ...d ▁in ▁using ▁visual ization ▁/ ▁dashboard...

### 144. Sample 144

- **Pred**: `▁with` (SKILL) [tokens 226:227]
- **Context**: ...▁Familia r ity ▁with ▁cloud ▁( Gen...

## Label Confusions

Predicted entities that overlap a gold entity but have the wrong type (SKILL vs TOOL).

### 1. Sample 146

- **Gold**: `, ▁E TL - Pro ze` (TOOL) [tokens 97:103]
- **Pred**: `, ▁E TL - Pro ze` (SKILL) [tokens 97:103]
- **Context**: ...▁Python , ▁SQL , ▁E TL - Pro ze ssen , ▁RA...

### 2. Sample 109

- **Gold**: `: ▁L LM ▁API` (TOOL) [tokens 67:71]
- **Pred**: `: ▁L LM ▁API` (SKILL) [tokens 67:71]
- **Context**: ...▁methods ▁such ▁as : ▁L LM ▁API s ▁and ▁agent...

### 3. Sample 109

- **Gold**: `▁and ▁agent ▁framework` (TOOL) [tokens 72:75]
- **Pred**: `▁and ▁agent ▁framework` (SKILL) [tokens 72:75]
- **Context**: ...LM ▁API s ▁and ▁agent ▁framework s ▁Ve ctor...

### 4. Sample 109

- **Gold**: `▁and ▁re trie val - based ▁approach` (TOOL) [tokens 80:87]
- **Pred**: `▁and ▁re trie val - based ▁approach` (SKILL) [tokens 80:87]
- **Context**: ...ctor ▁database s ▁and ▁re trie val - based ▁approach es ▁Evalua tion...

### 5. Sample 17

- **Gold**: `▁with ▁Ne st` (SKILL) [tokens 77:80]
- **Pred**: `▁with ▁Ne st` (TOOL) [tokens 77:80]
- **Context**: ...▁of ▁relevant ▁experience ▁with ▁Ne st JS ▁Under standing...

### 6. Sample 147

- **Gold**: `▁with` (SKILL) [tokens 43:44]
- **Pred**: `▁with` (TOOL) [tokens 43:44]
- **Context**: ...’ re ▁familiar ▁with ▁Python ▁as ▁well...

### 7. Sample 147

- **Gold**: `▁as ▁pan` (SKILL) [tokens 47:49]
- **Pred**: `▁as ▁pan` (TOOL) [tokens 47:49]
- **Context**: ...▁Python ▁as ▁well ▁as ▁pan das , ▁sci...

### 8. Sample 147

- **Gold**: `, ▁sci kit - le ar` (SKILL) [tokens 50:56]
- **Pred**: `, ▁sci kit - le ar` (TOOL) [tokens 50:56]
- **Context**: ...▁as ▁pan das , ▁sci kit - le ar n ▁and /...

### 9. Sample 147

- **Gold**: `. ▁E TL ▁pipe` (TOOL) [tokens 63:67]
- **Pred**: `. ▁E TL ▁pipe` (SKILL) [tokens 63:67]
- **Context**: ...▁L LM s . ▁E TL ▁pipe lines ▁and ▁agenti...

### 10. Sample 77

- **Gold**: `▁with ▁Unity ▁Catalog` (SKILL) [tokens 96:99]
- **Pred**: `▁with ▁Unity ▁Catalog` (TOOL) [tokens 96:99]
- **Context**: ...ly , ▁experience ▁with ▁Unity ▁Catalog ue , ▁A...

### 11. Sample 77

- **Gold**: `, ▁A sset ▁Bund` (SKILL) [tokens 100:104]
- **Pred**: `, ▁A sset ▁Bund` (TOOL) [tokens 100:104]
- **Context**: ...▁Unity ▁Catalog ue , ▁A sset ▁Bund les , ▁work...

### 12. Sample 77

- **Gold**: `, ▁work space` (SKILL) [tokens 105:108]
- **Pred**: `, ▁work space` (TOOL) [tokens 105:108]
- **Context**: ...sset ▁Bund les , ▁work space ▁creation , ▁...

### 13. Sample 77

- **Gold**: `▁of` (TOOL) [tokens 145:146]
- **Pred**: `▁of` (SKILL) [tokens 145:146]
- **Context**: ...▁) ▁Advanced ▁knowledge ▁of ▁Linux ▁/ ▁operating...

### 14. Sample 77

- **Gold**: `▁on ▁Data bric` (TOOL) [tokens 219:222]
- **Pred**: `▁on ▁Data bric` (SKILL) [tokens 219:222]
- **Context**: ...▁Machine ▁Learning ▁Engineering ▁on ▁Data bric ks ▁Experience ▁in...

### 15. Sample 37

- **Gold**: `. ▁Python ▁oder` (SKILL) [tokens 75:78]
- **Pred**: `.` (TOOL) [tokens 75:76]
- **Context**: ...▁z . B . ▁Python ▁oder ▁R ▁- ▁Erfahrung...

### 16. Sample 69

- **Gold**: `▁in` (SKILL) [tokens 32:33]
- **Pred**: `▁in` (TOOL) [tokens 32:33]
- **Context**: ...▁- ▁Strong ▁skills ▁in ▁Python ▁- ▁...

### 17. Sample 79

- **Gold**: `▁( NN` (TOOL) [tokens 35:37]
- **Pred**: `▁( NN` (SKILL) [tokens 35:37]
- **Context**: ...▁in ▁machine ▁learning ▁( NN s , ▁L...

### 18. Sample 79

- **Gold**: `, ▁L VM` (TOOL) [tokens 38:41]
- **Pred**: `, ▁L VM` (SKILL) [tokens 38:41]
- **Context**: ...▁( NN s , ▁L VM s , ▁V...

### 19. Sample 79

- **Gold**: `, ▁V LA` (TOOL) [tokens 42:45]
- **Pred**: `, ▁V LA` (SKILL) [tokens 42:45]
- **Context**: ...▁L VM s , ▁V LA s ) ▁and...

### 20. Sample 65

- **Gold**: `▁with` (TOOL) [tokens 146:147]
- **Pred**: `▁with` (SKILL) [tokens 146:147]
- **Context**: ...▁basic ▁working ▁experience ▁with ▁Linux / Uni...

### 21. Sample 65

- **Gold**: `▁and` (SKILL) [tokens 301:302]
- **Pred**: `▁and` (TOOL) [tokens 301:302]
- **Context**: ...al ▁database s ▁and ▁SQL ▁( O...

### 22. Sample 132

- **Gold**: `,` (SKILL) [tokens 293:294]
- **Pred**: `,` (TOOL) [tokens 293:294]
- **Context**: ...H ado op , ▁Spark , ▁Air...

### 23. Sample 70

- **Gold**: `▁learning ▁framework` (TOOL) [tokens 75:77]
- **Pred**: `▁with ▁machine ▁learning ▁framework` (SKILL) [tokens 73:77]
- **Context**: ...▁experience ▁with ▁machine ▁learning ▁framework s , ▁M...

### 24. Sample 28

- **Gold**: `, ▁Cloud - Service` (SKILL) [tokens 229:233]
- **Pred**: `, ▁Cloud - Service` (TOOL) [tokens 229:233]
- **Context**: ...▁Python , ▁SQL , ▁Cloud - Service s , ▁a...

### 25. Sample 16

- **Gold**: `▁both` (SKILL) [tokens 104:105]
- **Pred**: `▁both` (TOOL) [tokens 104:105]
- **Context**: ...WS ▁services ▁and ▁both ▁SQL ▁and ▁No...

### 26. Sample 16

- **Gold**: `▁and ▁No` (SKILL) [tokens 106:108]
- **Pred**: `▁and ▁No` (TOOL) [tokens 106:108]
- **Context**: ...▁and ▁both ▁SQL ▁and ▁No SQL ▁( e...

### 27. Sample 144

- **Gold**: `, ▁Trans former` (SKILL) [tokens 128:131]
- **Pred**: `, ▁Trans former` (TOOL) [tokens 128:131]
- **Context**: .... g . , ▁Trans former s , ▁...

### 28. Sample 144

- **Gold**: `▁ RL` (SKILL) [tokens 133:135]
- **Pred**: `▁ RL` (TOOL) [tokens 133:135]
- **Context**: ...former s , ▁ RL HF , ▁fine...

## Boundary Errors

Predicted entities that overlap a gold entity with the correct type but wrong boundaries.

### 1. Sample 33

- **Gold**: `, ▁robot` (SKILL) [tokens 16:18]
- **Pred**: `,` (SKILL) [tokens 16:17]
- **Context**: ...▁in ▁computer ▁science , ▁robot ics , ▁electric...

### 2. Sample 33

- **Gold**: `, ▁electric al` (SKILL) [tokens 19:22]
- **Pred**: `,` (SKILL) [tokens 19:20]
- **Context**: ..., ▁robot ics , ▁electric al ▁engineering , ▁or...

### 3. Sample 33

- **Gold**: `▁in ▁robot` (SKILL) [tokens 31:33]
- **Pred**: `▁in` (SKILL) [tokens 31:32]
- **Context**: ...▁5 + ▁years ▁in ▁robot ics ▁or ▁applied...

### 4. Sample 33

- **Gold**: `▁or ▁mobile ▁robot` (SKILL) [tokens 47:50]
- **Pred**: `▁or` (SKILL) [tokens 47:48]
- **Context**: ...▁in ▁manipula tion ▁or ▁mobile ▁robot ics . ▁Deep...

### 5. Sample 33

- **Gold**: `, ▁reason ing ▁and ▁vision - language - action` (SKILL) [tokens 63:72]
- **Pred**: `, ▁reason` (SKILL) [tokens 63:65]
- **Context**: ...▁multi mo dal , ▁reason ing ▁and ▁vision - language - action ▁models , ▁dif...

### 6. Sample 33

- **Gold**: `▁modern ▁fine tu ning` (SKILL) [tokens 79:83]
- **Pred**: `▁fine tu` (SKILL) [tokens 80:82]
- **Context**: ...▁models , ▁and ▁modern ▁fine tu ning ▁methods ▁( PE...

### 7. Sample 33

- **Gold**: `▁( PE` (SKILL) [tokens 84:86]
- **Pred**: `PE` (SKILL) [tokens 85:86]
- **Context**: ...tu ning ▁methods ▁( PE FT , ▁D...

### 8. Sample 33

- **Gold**: `, ▁D` (SKILL) [tokens 87:89]
- **Pred**: `▁D` (SKILL) [tokens 88:89]
- **Context**: ...▁( PE FT , ▁D PO , ▁...

### 9. Sample 33

- **Gold**: `▁ RL` (SKILL) [tokens 91:93]
- **Pred**: `▁` (SKILL) [tokens 91:92]
- **Context**: ...▁D PO , ▁ RL HF ). ▁Strong...

### 10. Sample 33

- **Gold**: `▁of ▁ki ne matic` (SKILL) [tokens 155:159]
- **Pred**: `▁of ▁ki ne` (SKILL) [tokens 155:158]
- **Context**: ...Co ); ▁knowledge ▁of ▁ki ne matic s , ▁motion...

### 11. Sample 146

- **Gold**: `▁im ▁Data` (SKILL) [tokens 57:59]
- **Pred**: `▁im` (SKILL) [tokens 57:58]
- **Context**: ...▁in ▁Projekt en ▁im ▁Data ▁Science , ▁...

### 12. Sample 146

- **Gold**: `, ▁RA` (TOOL) [tokens 104:106]
- **Pred**: `,` (TOOL) [tokens 104:105]
- **Context**: ...Pro ze ssen , ▁RA G , ▁...

### 13. Sample 146

- **Gold**: `▁ ML /` (TOOL) [tokens 108:111]
- **Pred**: `/` (TOOL) [tokens 110:111]
- **Context**: ...▁RA G , ▁ ML / DL , ▁L...

### 14. Sample 146

- **Gold**: `, ▁L LM` (TOOL) [tokens 112:115]
- **Pred**: `,` (TOOL) [tokens 112:113]
- **Context**: ...ML / DL , ▁L LM s , ▁Panda...

### 15. Sample 109

- **Gold**: `▁in ▁Data` (SKILL) [tokens 8:10]
- **Pred**: `▁in` (SKILL) [tokens 8:9]
- **Context**: ...▁of ▁professional ▁experience ▁in ▁Data ▁Science , ▁N...

### 16. Sample 109

- **Gold**: `▁and ▁L` (SKILL) [tokens 50:52]
- **Pred**: `▁and ▁L LM -` (SKILL) [tokens 50:54]
- **Context**: ...▁N LP - ▁and ▁L LM - based...

### 17. Sample 109

- **Gold**: `▁ ML ▁framework` (SKILL) [tokens 100:103]
- **Pred**: `▁` (SKILL) [tokens 100:101]
- **Context**: ...▁knowledge ▁of ▁modern ▁ ML ▁framework s ▁( e...

### 18. Sample 109

- **Gold**: `▁with ▁cloud - based ▁ architecture` (SKILL) [tokens 144:150]
- **Pred**: `▁with ▁cloud -` (SKILL) [tokens 144:147]
- **Context**: ...▁production ▁code ▁Experience ▁with ▁cloud - based ▁ architecture s ▁and ▁M...

### 19. Sample 109

- **Gold**: `▁and ▁M LO` (SKILL) [tokens 151:154]
- **Pred**: `▁and ▁M LO ps` (SKILL) [tokens 151:155]
- **Context**: ...▁ architecture s ▁and ▁M LO ps ▁/ ▁de...

### 20. Sample 17

- **Gold**: `▁one ▁Cloud ▁Services ▁Provide` (SKILL) [tokens 47:51]
- **Pred**: `▁one ▁Cloud` (SKILL) [tokens 47:49]
- **Context**: ...▁in ▁at ▁least ▁one ▁Cloud ▁Services ▁Provide r ▁Mono re...

### 21. Sample 17

- **Gold**: `r ▁Mono re po ▁ architecture` (SKILL) [tokens 51:57]
- **Pred**: `r ▁Mono re` (SKILL) [tokens 51:54]
- **Context**: ...▁Cloud ▁Services ▁Provide r ▁Mono re po ▁ architecture s ▁and ▁tool...

### 22. Sample 147

- **Gold**: `. ▁Big` (SKILL) [tokens 78:80]
- **Pred**: `.` (SKILL) [tokens 78:79]
- **Context**: ...▁new ▁to ▁you . ▁Big ▁data , ▁data...

### 23. Sample 147

- **Gold**: `, ▁data ▁ analytic` (SKILL) [tokens 81:85]
- **Pred**: `, ▁data ▁` (SKILL) [tokens 81:84]
- **Context**: .... ▁Big ▁data , ▁data ▁ analytic s , ▁and...

### 24. Sample 147

- **Gold**: `▁and ▁process ▁mi` (SKILL) [tokens 87:90]
- **Pred**: `▁and ▁process` (SKILL) [tokens 87:89]
- **Context**: ...analytic s , ▁and ▁process ▁mi ning ▁make ▁your...

### 25. Sample 147

- **Gold**: `▁and` (SKILL) [tokens 169:170]
- **Pred**: `▁and ▁SQL` (SKILL) [tokens 169:171]
- **Context**: ..., ▁Oracle ) ▁and ▁SQL ▁skills ....

### 26. Sample 86

- **Gold**: `▁` (SKILL) [tokens 52:53]
- **Pred**: `▁ ML - H inter` (SKILL) [tokens 52:57]
- **Context**: ...prä g tem ▁ ML - H...

### 27. Sample 86

- **Gold**: `igen ▁Machine` (SKILL) [tokens 95:97]
- **Pred**: `igen ▁Machine ▁Learning - Biblio` (SKILL) [tokens 95:100]
- **Context**: ...▁den ▁ gäng igen ▁Machine ▁Learning - Biblio...

### 28. Sample 86

- **Gold**: `▁mit ▁M LO ps - Tool` (SKILL) [tokens 104:110]
- **Pred**: `▁mit ▁M LO` (SKILL) [tokens 104:107]
- **Context**: ...ken ▁sowie ▁Erfahrungen ▁mit ▁M LO ps - Tool s ▁wie ▁...

### 29. Sample 86

- **Gold**: `▁im ▁Einsatz ▁von ▁Infra structure ▁as ▁Code ▁( Ter ra form , ▁ARM` (SKILL) [tokens 139:152]
- **Pred**: `▁von ▁Infra structure ▁as` (SKILL) [tokens 141:145]
- **Context**: ...men gen ▁sowie ▁im ▁Einsatz ▁von ▁Infra structure ▁as ▁Code ▁( Ter ra form , ▁ARM ). ▁Team fähigkeit...

### 30. Sample 77

- **Gold**: `▁in ▁software` (SKILL) [tokens 65:67]
- **Pred**: `▁in` (SKILL) [tokens 65:66]
- **Context**: ...▁Very ▁good ▁skills ▁in ▁software ▁development ▁with ▁at...

### 31. Sample 77

- **Gold**: `▁of` (SKILL) [tokens 118:119]
- **Pred**: `▁of ▁SQL` (SKILL) [tokens 118:120]
- **Context**: ...base ▁Good ▁knowledge ▁of ▁SQL ▁& ▁database...

### 32. Sample 77

- **Gold**: `▁ ML / Data` (SKILL) [tokens 243:247]
- **Pred**: `▁` (SKILL) [tokens 243:244]
- **Context**: ...ive ▁operation ▁of ▁ ML / Data ▁services ▁Experience ▁in...

### 33. Sample 37

- **Gold**: `▁( Hy pot hes entes` (SKILL) [tokens 14:19]
- **Pred**: `▁(` (SKILL) [tokens 14:15]
- **Context**: ...▁statisti schen ▁Verfahren ▁( Hy pot hes entes ts , ▁Sign...

### 34. Sample 37

- **Gold**: `▁mit ▁Datenbank systemen ▁und` (SKILL) [tokens 37:41]
- **Pred**: `▁mit ▁Datenbank` (SKILL) [tokens 37:39]
- **Context**: ...▁Sicher er ▁Umgang ▁mit ▁Datenbank systemen ▁und ▁SQL ▁- ▁Kenntnis...

### 35. Sample 37

- **Gold**: `, ▁Öko n ometri` (SKILL) [tokens 143:147]
- **Pred**: `,` (SKILL) [tokens 143:144]
- **Context**: ..., ▁Betriebs wirtschaft , ▁Öko n ometri e , ▁Mathematik...

### 36. Sample 37

- **Gold**: `▁oder ▁Informati` (SKILL) [tokens 150:152]
- **Pred**: `▁oder` (SKILL) [tokens 150:151]
- **Context**: ...e , ▁Mathematik ▁oder ▁Informati k ▁oder ▁eine...

### 37. Sample 69

- **Gold**: `▁/ ▁Sup a base ▁R EST ▁API` (TOOL) [tokens 64:71]
- **Pred**: `▁/ ▁Sup a base` (TOOL) [tokens 64:68]
- **Context**: ...g RES T ▁/ ▁Sup a base ▁R EST ▁API s ▁) ▁-...

### 38. Sample 79

- **Gold**: `▁of ▁classic al ▁and ▁modern ▁control` (SKILL) [tokens 117:123]
- **Pred**: `▁of` (SKILL) [tokens 117:118]
- **Context**: ...). ▁Strong ▁understanding ▁of ▁classic al ▁and ▁modern ▁control ▁theory , ▁loco...

### 39. Sample 79

- **Gold**: `, ▁loco motion ▁dynamic` (SKILL) [tokens 124:128]
- **Pred**: `, ▁loco motion` (SKILL) [tokens 124:127]
- **Context**: ...▁modern ▁control ▁theory , ▁loco motion ▁dynamic s , ▁etc...

### 40. Sample 65

- **Gold**: `/ Uni x - based` (TOOL) [tokens 148:153]
- **Pred**: `/` (TOOL) [tokens 148:149]
- **Context**: ...▁experience ▁with ▁Linux / Uni x - based ▁OS ▁or ▁Do...

### 41. Sample 65

- **Gold**: `▁using ▁Gen` (SKILL) [tokens 166:168]
- **Pred**: `▁using ▁Gen AI` (SKILL) [tokens 166:169]
- **Context**: ...et ence ▁in ▁using ▁Gen AI ▁models ▁for...

### 42. Sample 132

- **Gold**: `▁and ▁data ▁pipe` (SKILL) [tokens 85:88]
- **Pred**: `▁pipe` (SKILL) [tokens 87:88]
- **Context**: ...▁new ▁ ML ▁and ▁data ▁pipe lines , ▁as...

### 43. Sample 132

- **Gold**: `▁and ▁data ▁pipe` (SKILL) [tokens 98:101]
- **Pred**: `▁pipe` (SKILL) [tokens 100:101]
- **Context**: ...▁existing ▁ ML ▁and ▁data ▁pipe lines . ▁...

### 44. Sample 132

- **Gold**: `▁creating ▁automat ed ▁tu ning ▁and ▁out lier ▁det ection ▁algorithm` (SKILL) [tokens 134:145]
- **Pred**: `▁automat ed ▁tu` (SKILL) [tokens 135:138]
- **Context**: ...▁as ▁well ▁as ▁creating ▁automat ed ▁tu ning ▁and ▁out lier ▁det ection ▁algorithm s . ▁Partner...

### 45. Sample 70

- **Gold**: `▁with ▁machine` (SKILL) [tokens 73:75]
- **Pred**: `▁with ▁machine ▁learning ▁framework` (SKILL) [tokens 73:77]
- **Context**: ...- on ▁experience ▁with ▁machine ▁learning ▁framework s...

### 46. Sample 70

- **Gold**: `, ▁M LO ps ▁practice` (SKILL) [tokens 78:83]
- **Pred**: `, ▁M LO` (SKILL) [tokens 78:81]
- **Context**: ...▁learning ▁framework s , ▁M LO ps ▁practice s , ▁and...

### 47. Sample 10

- **Gold**: `▁with` (SKILL) [tokens 118:119]
- **Pred**: `▁with ▁AI /` (SKILL) [tokens 118:121]
- **Context**: ...▁and ▁familiar ity ▁with ▁AI / ML...

### 48. Sample 57

- **Gold**: `, ▁Team` (SKILL) [tokens 43:45]
- **Pred**: `, ▁Team führung` (SKILL) [tokens 43:46]
- **Context**: ...ische ▁Modell ierung , ▁Team führung ▁und ▁Men...

### 49. Sample 83

- **Gold**: `▁and ▁GPU ▁ architecture ▁fundamental` (SKILL) [tokens 111:116]
- **Pred**: `▁and` (SKILL) [tokens 111:112]
- **Context**: ...▁expertise ▁with ▁CPU ▁and ▁GPU ▁ architecture ▁fundamental s . ▁Effective...

### 50. Sample 83

- **Gold**: `▁of ▁linear ▁al ge` (SKILL) [tokens 176:180]
- **Pred**: `▁al` (SKILL) [tokens 178:179]
- **Context**: .... ▁Excellent ▁understanding ▁of ▁linear ▁al ge bra . </s>...

### 51. Sample 105

- **Gold**: `: ▁Software` (SKILL) [tokens 10:12]
- **Pred**: `:` (SKILL) [tokens 10:11]
- **Context**: ...▁Talent e ▁suchen : ▁Software entwicklung ▁: ▁Ent...

### 52. Sample 105

- **Gold**: `. ▁Kü n st liche ▁Intel ligen z ▁und ▁Machine` (SKILL) [tokens 69:79]
- **Pred**: `. ▁Kü n st liche ▁Intel ligen` (SKILL) [tokens 69:76]
- **Context**: ..., ▁flexible ▁Lösungen . ▁Kü n st liche ▁Intel ligen z ▁und ▁Machine ▁Learning ▁: ▁Entwicklung...

### 53. Sample 105

- **Gold**: `. ▁Cyber` (SKILL) [tokens 101:103]
- **Pred**: `.` (SKILL) [tokens 101:102]
- **Context**: ...▁Lösungen ▁zu ▁schaffen . ▁Cyber security ▁: ▁Arbeit...

### 54. Sample 105

- **Gold**: `. ▁Big ▁Data ▁und ▁Data` (SKILL) [tokens 128:133]
- **Pred**: `. ▁Big` (SKILL) [tokens 128:130]
- **Context**: ...▁Bed roh ungen . ▁Big ▁Data ▁und ▁Data ▁Science ▁: ▁Nutzung...

### 55. Sample 105

- **Gold**: `. ▁Dev Op s ▁und ▁IT - In fra` (SKILL) [tokens 192:201]
- **Pred**: `. ▁Dev Op` (SKILL) [tokens 192:195]
- **Context**: ...▁Android ▁und ▁iOS . ▁Dev Op s ▁und ▁IT - In fra struktur ▁: ▁Mit...

### 56. Sample 105

- **Gold**: `. ▁A gile ▁Software` (SKILL) [tokens 219:223]
- **Pred**: `.` (SKILL) [tokens 219:220]
- **Context**: ...▁und ▁Infrastruktur en . ▁A gile ▁Software entwicklung ▁: ▁Anwendung...

### 57. Sample 105

- **Gold**: `▁der ▁Software` (SKILL) [tokens 315:317]
- **Pred**: `▁der` (SKILL) [tokens 315:316]
- **Context**: ...erweise ▁Erfahrung ▁in ▁der ▁Software entwicklung ▁oder ▁ver...

### 58. Sample 28

- **Gold**: `, ▁Data ▁S cient` (SKILL) [tokens 54:58]
- **Pred**: `▁S` (SKILL) [tokens 56:57]
- **Context**: ...▁Software ▁Engine er , ▁Data ▁S cient ist ). ▁Ver...

### 59. Sample 28

- **Gold**: `, ▁Software ▁Engine` (SKILL) [tokens 112:115]
- **Pred**: `,` (SKILL) [tokens 112:113]
- **Context**: ...- Consult ant , ▁Software ▁Engine er , ▁Data...

### 60. Sample 16

- **Gold**: `▁in ▁software ▁quality ▁` (SKILL) [tokens 14:18]
- **Pred**: `▁in ▁software` (SKILL) [tokens 14:16]
- **Context**: ...▁of ▁professional ▁experience ▁in ▁software ▁quality ▁ assurance ▁or ▁engineering...

### 61. Sample 16

- **Gold**: `.` (SKILL) [tokens 88:89]
- **Pred**: `. ▁Cloud` (SKILL) [tokens 88:90]
- **Context**: ...▁Py S park . ▁Cloud ▁& ▁Database...

### 62. Sample 16

- **Gold**: `▁with ▁A` (TOOL) [tokens 99:101]
- **Pred**: `▁with ▁A WS` (TOOL) [tokens 99:102]
- **Context**: ...▁Familia r ity ▁with ▁A WS ▁services ▁and...

### 63. Sample 16

- **Gold**: `▁( Super vis` (SKILL) [tokens 179:182]
- **Pred**: `▁( Super vis ed / Re in force ment` (SKILL) [tokens 179:188]
- **Context**: ...▁of ▁Machine ▁Learning ▁( Super vis ed / Re...

### 64. Sample 16

- **Gold**: `/ Re in force ment` (SKILL) [tokens 183:188]
- **Pred**: `▁( Super vis ed / Re in force ment` (SKILL) [tokens 179:188]
- **Context**: ...Super vis ed / Re in force ment ▁Learning ), ▁Pred...

### 65. Sample 16

- **Gold**: `, ▁Audi ence` (SKILL) [tokens 233:236]
- **Pred**: `,` (SKILL) [tokens 233:234]
- **Context**: ...D SP s , ▁Audi ence ▁Data , ▁Frau...

### 66. Sample 144

- **Gold**: `, ▁data` (SKILL) [tokens 10:12]
- **Pred**: `▁data` (SKILL) [tokens 11:12]
- **Context**: ...▁in ▁computer ▁science , ▁data ▁engineering , ▁ma...

### 67. Sample 144

- **Gold**: `▁with ▁( Gen )` (SKILL) [tokens 102:106]
- **Pred**: `▁( Gen )` (SKILL) [tokens 103:106]
- **Context**: ...▁monitor ▁these ▁Experience ▁with ▁( Gen ) AI , ▁L...

### 68. Sample 144

- **Gold**: `, ▁L` (SKILL) [tokens 107:109]
- **Pred**: `, ▁L LM ▁framework` (SKILL) [tokens 107:111]
- **Context**: ...Gen ) AI , ▁L LM ▁framework s...

### 69. Sample 144

- **Gold**: `, ▁fine - tu` (SKILL) [tokens 136:140]
- **Pred**: `▁fine - tu` (SKILL) [tokens 137:140]
- **Context**: ...▁ RL HF , ▁fine - tu ning ) ▁Strong...

### 70. Sample 144

- **Gold**: `ying ▁( Gen )` (SKILL) [tokens 190:194]
- **Pred**: `)` (SKILL) [tokens 193:194]
- **Context**: ...▁Experience ▁de plo ying ▁( Gen ) AI ▁pipe lines...

### 71. Sample 144

- **Gold**: `, ▁ve ctor ▁database` (SKILL) [tokens 213:217]
- **Pred**: `, ▁ve ctor` (SKILL) [tokens 213:216]
- **Context**: ...trie val ▁systems , ▁ve ctor ▁database s ) ▁into...

### 72. Sample 144

- **Gold**: `▁cloud ▁( Gen )` (SKILL) [tokens 227:231]
- **Pred**: `▁( Gen ) AI` (SKILL) [tokens 228:232]
- **Context**: ...r ity ▁with ▁cloud ▁( Gen ) AI ▁platform s...
