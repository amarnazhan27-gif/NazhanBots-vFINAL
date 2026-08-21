//+------------------------------------------------------------------+
//| AURUM_HFM_CENT_PREFLIGHT.mq5                                    |
//| Read-only HFM Cent Gold environment and capital feasibility probe|
//+------------------------------------------------------------------+
#property strict
#property version "1.03"
#property script_show_inputs

input string InpGoldSymbol                 = "XAUUSDc";
input double InpExpectedContractSize       = 1.00;
input double InpContractTolerance          = 0.05;
input double InpExpectedMinimumLot         = 0.01;
input double InpExpectedVolumeStep         = 0.01;
input double InpTargetRiskPct              = 0.10;
input double InpReferenceEquityUSC         = 100.00;
input int    InpAtrPeriod                  = 14;

string BoolText(const bool value)
  {
   return value ? "PASS" : "FAIL";
  }

bool ContainsHfmIdentity(const string server,const string company)
  {
   string identity=server+" "+company;
   StringToUpper(identity);
   return StringFind(identity,"HFM") >= 0 ||
          StringFind(identity,"HF MARKETS") >= 0 ||
          StringFind(identity,"HFMARKETS") >= 0 ||
          StringFind(identity,"HOTFOREX") >= 0;
  }

bool NearlyEqual(const double lhs,const double rhs,const double tolerance)
  {
   return MathAbs(lhs-rhs) <= MathMax(0.0,tolerance);
  }

bool EndsWithCentSuffix(const string symbol)
  {
   int length=StringLen(symbol);
   if(length < 2) return false;
   string suffix=StringSubstr(symbol,length-1,1);
   StringToUpper(suffix);
   return suffix == "C";
  }

bool SimpleAtr(const string symbol,const ENUM_TIMEFRAMES timeframe,const int period,double &atr)
  {
   atr=0.0;
   int count=MathMax(2,period+1);
   MqlRates rates[];
   ArraySetAsSeries(rates,true);
   int copied=CopyRates(symbol,timeframe,1,count,rates);
   if(copied < count) return false;
   double sum=0.0;
   for(int i=0;i<period;i++)
     {
      double previousClose=rates[i+1].close;
      double trueRange=MathMax(rates[i].high-rates[i].low,
                               MathMax(MathAbs(rates[i].high-previousClose),
                                       MathAbs(rates[i].low-previousClose)));
      sum+=trueRange;
     }
   atr=sum/period;
   return atr > 0.0 && MathIsValidNumber(atr);
  }

double MinimumLotRisk(const string symbol,const double volume,const double entry,
                      const double stopDistance,double &riskPct,string &method)
  {
   riskPct=0.0;
   method="UNAVAILABLE";
   double profit=0.0;
   if(volume <= 0.0 || entry <= 0.0 || stopDistance <= 0.0)
      return -1.0;

   double risk=0.0;
   if(OrderCalcProfit(ORDER_TYPE_BUY,symbol,volume,entry,entry-stopDistance,profit) &&
      MathIsValidNumber(profit) && MathAbs(profit) > 0.0)
     {
      risk=MathAbs(profit);
      method="ORDER_CALC_PROFIT";
     }
   else
     {
      // HFM may not publish a current USDUSC conversion quote during terminal
      // startup. For the exact validated Cent environment, USD P/L converts to
      // USC at 100 cents per dollar. Keep this probe-only fallback tightly
      // constrained and fail closed everywhere else.
      string accountCurrency=AccountInfoString(ACCOUNT_CURRENCY);
      string profitCurrency=SymbolInfoString(symbol,SYMBOL_CURRENCY_PROFIT);
      double contract=SymbolInfoDouble(symbol,SYMBOL_TRADE_CONTRACT_SIZE);
      if(accountCurrency != "USC" || profitCurrency != "USD" || contract <= 0.0)
         return -1.0;
      risk=stopDistance*contract*volume*100.0;
      if(!MathIsValidNumber(risk) || risk <= 0.0)
         return -1.0;
      method="USD_TO_USC_X100_FALLBACK";
     }

   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity > 0.0) riskPct=risk/equity*100.0;
   return risk;
  }

void Emit(const string key,const string value)
  {
   Print("AURUM_PREFLIGHT|",key,"=",value);
  }

void OnStart()
  {
   string server=AccountInfoString(ACCOUNT_SERVER);
   string company=AccountInfoString(ACCOUNT_COMPANY);
   string currency=AccountInfoString(ACCOUNT_CURRENCY);
   ENUM_ACCOUNT_TRADE_MODE accountMode=(ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   string mode=(accountMode == ACCOUNT_TRADE_MODE_REAL ? "REAL" :
                accountMode == ACCOUNT_TRADE_MODE_DEMO ? "DEMO" : "CONTEST");
   bool symbolSelected=SymbolSelect(InpGoldSymbol,true);
   bool hfm=ContainsHfmIdentity(server,company);
   bool usc=(currency == "USC");
   bool suffix=EndsWithCentSuffix(InpGoldSymbol);

   Emit("BEGIN","version=1.03");
   Emit("ACCOUNT_MODE",mode);
   Emit("SERVER",server);
   Emit("COMPANY",company);
   Emit("CURRENCY",currency);
   Emit("CHECK_HFM_IDENTITY",BoolText(hfm));
   Emit("CHECK_USC",BoolText(usc));
   Emit("CHECK_SYMBOL_SELECTED",BoolText(symbolSelected));
   Emit("CHECK_CENT_SUFFIX",BoolText(suffix));

   if(!symbolSelected)
     {
      Emit("OVERALL","FAIL|reason=SYMBOL_NOT_AVAILABLE");
      return;
     }

   double contract=SymbolInfoDouble(InpGoldSymbol,SYMBOL_TRADE_CONTRACT_SIZE);
   double minimum=SymbolInfoDouble(InpGoldSymbol,SYMBOL_VOLUME_MIN);
   double step=SymbolInfoDouble(InpGoldSymbol,SYMBOL_VOLUME_STEP);
   double maximum=SymbolInfoDouble(InpGoldSymbol,SYMBOL_VOLUME_MAX);
   double tickSize=SymbolInfoDouble(InpGoldSymbol,SYMBOL_TRADE_TICK_SIZE);
   double tickValue=SymbolInfoDouble(InpGoldSymbol,SYMBOL_TRADE_TICK_VALUE);
   string profitCurrency=SymbolInfoString(InpGoldSymbol,SYMBOL_CURRENCY_PROFIT);
   long stopsLevel=SymbolInfoInteger(InpGoldSymbol,SYMBOL_TRADE_STOPS_LEVEL);
   long freezeLevel=SymbolInfoInteger(InpGoldSymbol,SYMBOL_TRADE_FREEZE_LEVEL);
   long tradeMode=SymbolInfoInteger(InpGoldSymbol,SYMBOL_TRADE_MODE);
   bool contractOk=NearlyEqual(contract,InpExpectedContractSize,InpContractTolerance);
   bool minimumOk=NearlyEqual(minimum,InpExpectedMinimumLot,0.000001);
   bool stepOk=NearlyEqual(step,InpExpectedVolumeStep,0.000001);
   bool tradeable=(tradeMode == SYMBOL_TRADE_MODE_FULL ||
                   tradeMode == SYMBOL_TRADE_MODE_LONGONLY ||
                   tradeMode == SYMBOL_TRADE_MODE_SHORTONLY);

   Emit("CONTRACT_SIZE",DoubleToString(contract,4));
   Emit("VOLUME_MIN",DoubleToString(minimum,4));
   Emit("VOLUME_STEP",DoubleToString(step,4));
   Emit("VOLUME_MAX",DoubleToString(maximum,2));
   Emit("TICK_SIZE",DoubleToString(tickSize,5));
   Emit("TICK_VALUE",DoubleToString(tickValue,5));
   Emit("PROFIT_CURRENCY",profitCurrency);
   Emit("STOPS_LEVEL",IntegerToString((int)stopsLevel));
   Emit("FREEZE_LEVEL",IntegerToString((int)freezeLevel));
   Emit("CHECK_CONTRACT",BoolText(contractOk));
   Emit("CHECK_MINIMUM_LOT",BoolText(minimumOk));
   Emit("CHECK_VOLUME_STEP",BoolText(stepOk));
   Emit("CHECK_TRADE_MODE",BoolText(tradeable));

   MqlTick tick={};
   bool tickOk=SymbolInfoTick(InpGoldSymbol,tick) && tick.ask > tick.bid && tick.bid > 0.0;
   Emit("CHECK_TICK",BoolText(tickOk));
   if(!tickOk)
     {
      Emit("OVERALL","FAIL|reason=NO_VALID_TICK");
      return;
     }

   double spread=tick.ask-tick.bid;
   double atrM1=0.0,atrM5=0.0;
   bool atrM1Ok=SimpleAtr(InpGoldSymbol,PERIOD_M1,InpAtrPeriod,atrM1);
   bool atrM5Ok=SimpleAtr(InpGoldSymbol,PERIOD_M5,InpAtrPeriod,atrM5);
   double point=SymbolInfoDouble(InpGoldSymbol,SYMBOL_POINT);
   double stopDistance=MathMax(4.0*spread,(double)stopsLevel*point);
   if(atrM1Ok) stopDistance=MathMax(stopDistance,1.20*atrM1);
   double minimumRiskPct=0.0;
   string riskMethod="UNAVAILABLE";
   double minimumRisk=MinimumLotRisk(InpGoldSymbol,minimum,tick.ask,stopDistance,
                                     minimumRiskPct,riskMethod);
   double requiredEquity=(minimumRisk > 0.0 && InpTargetRiskPct > 0.0 ?
                          minimumRisk/(InpTargetRiskPct/100.0) : 0.0);
   double referenceRiskPct=(minimumRisk > 0.0 && InpReferenceEquityUSC > 0.0 ?
                            minimumRisk/InpReferenceEquityUSC*100.0 : 0.0);
   bool currentEquityAvailable=(AccountInfoDouble(ACCOUNT_EQUITY) > 0.0);

   Emit("SPREAD_PRICE",DoubleToString(spread,5));
   Emit("ATR_M1",atrM1Ok ? DoubleToString(atrM1,5) : "UNAVAILABLE");
   Emit("ATR_M5",atrM5Ok ? DoubleToString(atrM5,5) : "UNAVAILABLE");
   Emit("MODEL_STOP_DISTANCE",DoubleToString(stopDistance,5));
   Emit("RISK_CALC_METHOD",riskMethod);
   Emit("MIN_LOT_RISK_ACCOUNT_CCY",DoubleToString(minimumRisk,4));
   Emit("MIN_LOT_RISK_PCT",DoubleToString(minimumRiskPct,4));
   Emit("CURRENT_EQUITY_AVAILABLE",BoolText(currentEquityAvailable));
   Emit("REFERENCE_EQUITY_USC",DoubleToString(InpReferenceEquityUSC,2));
   Emit("REFERENCE_MIN_LOT_RISK_PCT",DoubleToString(referenceRiskPct,4));
   Emit("REQUIRED_EQUITY_FOR_TARGET_RISK",DoubleToString(requiredEquity,2));

   bool capitalOk=(minimumRisk > 0.0 && referenceRiskPct > 0.0 &&
                   referenceRiskPct <= InpTargetRiskPct*1.05);
   Emit("CHECK_CAPITAL_FOR_TARGET_RISK",BoolText(capitalOk));
   bool overall=hfm && usc && suffix && contractOk && minimumOk && stepOk &&
                tradeable && tickOk && atrM1Ok && atrM5Ok && capitalOk;
   Emit("OVERALL",BoolText(overall));
   Emit("END","no_trade_operations_performed=true");
  }
