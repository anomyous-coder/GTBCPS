This is for "An AI driven Autonomous Cashflow-based Stablecoins Design", providing a simulation of the proposed stablecoin-GTBCPS.

Installation:
Please run 
```shell
pip -r install requirement.txt`
```
Recommended python env: 3.8.20

Experiment:
The complete command is:
```shell
python run.py 
    --data_dir {data_dir} \
    --graph_dir {graph_dir} \
    --log_dir {log_dir} \
    --output {output_dir} \
    --confidence_score {confidence_score} \
    --total_issuance {total_issuance} \
    --pegged_price_in_usd {pegged_price_in_usd} \
    --collateral_ratio_gold {collateral_ratio_gold} \
    --fraction_of_hedged {fraction_of_hedged} \
    --single_redemption_amount {single_redemption_amount} \
    --liquidation_benchmark {liquidation_benchmark} \
    --liquidation_flag {liquidation_flag} \
    --with_learnings {with_learnings} \
    --display_payout_of_tranches {display_payout_of_tranches} \
```

- `data_dir`: type=str, default=`./data/`,  `directory of the original data.`  
- `graph_dir`, type=str, default=`./graph/`,  `directory of graphs.`
- `output_dir`, type=str, default=`./output/`,  `directory of outputs.`
- `log_dir`, type=str, default=`./log/`,  `directory of the transaction logs.`
- `confidence_score`,  type=float, default=1.96, `confidence score of predicted price.`
- `total_issuance`,  type=float, default=100000000, `GTBCPS's issuance price pegged to USD.`
- `pegged_price_in_usd`,  type=float, default=1.00, `Total issued value of the stablecoin.`
- `collateral_ratio_gold`,  type=float, default=0.80, `collateral value of gold to value of GTBCPS.`
- `fraction_of_hedged`, type=float, default=0.80, `set the fraction percentage of the interest risk to be hedged.Default to "100%".`
- `single_redemption_amount`, type=float, default=0.00, `amount of GTBCPS to be reddemed once.`
- `with_learnings`, type=bool, default=False,  `Bool type. True for auto-imputating and predicting missing data in original datasets.`
- `liquidation_benchmark`, type=float, default=0.8,  `Bottom line of total value of collaterals to trigger liquidation.`
- `liquidation_flag`, type=str, default=`No`,  `Indicator to trigger liquidation.`
- `display_payout_of_tranches`, type=str, default=`all`, `display pricing of specific tranches,  can be 1,  2,  3,  all or an array.`


The configuration file is in `./Config.py`,  you can change the parameters there.