//+------------------------------------------------------------------+
//|                    AURUM_CENT_ADAPTIVE_M1_DEMO.mq5               |
//|      Adaptive Gold Cent development EA - demo/tester only        |
//+------------------------------------------------------------------+
#property strict
#property version   "1.34"
#property description "H1 direction, M15 regime, M5 setup, M1 trigger"
#property description "HFM Cent validation; real use requires three explicit gates"

#define EA_NAME "AURUM_CENT_ADAPTIVE_M1_DEMO"

// A real account still requires the runtime switch and an exact account login.
// The distributed preset keeps real trading disabled.
const bool BUILD_ALLOW_REAL_ACCOUNT = false;

enum ENUM_AURUM_SESSION
  {
   AURUM_SESSION_BLOCKED = 0,
   AURUM_SESSION_ASIA,
   AURUM_SESSION_LONDON,
   AURUM_SESSION_NEW_YORK
  };

enum ENUM_AURUM_REGIME
  {
   AURUM_REGIME_UNKNOWN = 0,
   AURUM_REGIME_RANGE,
   AURUM_REGIME_TREND,
   AURUM_REGIME_HIGH_VOLATILITY,
   AURUM_REGIME_TRANSITION
  };

input group "=== Identity and account safety ==="
input ulong  InpMagicNumber               = 26081301;
input bool   InpAllowRealAccount          = false;
input long   InpAuthorizedRealLogin       = 0;
input bool   InpRequireCentCurrency        = true;
input bool   InpRequireHfmEnvironment      = true;
input double InpExpectedGoldContractSize   = 1.00;
input double InpContractSizeTolerance      = 0.05;

input group "=== Multi-timeframe strategy ==="
input int    InpH1EmaPeriod                = 200;
input int    InpM15FastEmaPeriod           = 20;
input int    InpM15SlowEmaPeriod           = 50;
input int    InpM15AdxPeriod               = 14;
input double InpM15MinimumAdx              = 30.0;
input int    InpAtrPeriod                  = 14;
input int    InpM5EmaPeriod                = 20;
input int    InpM1FastEmaPeriod            = 9;
input int    InpM1SlowEmaPeriod            = 20;
input double InpMinimumBodyFraction        = 0.35;
input double InpM5TouchAtrFraction         = 0.15;
input double InpHighVolatilityMultiplier   = 1.80;

input group "=== Calendar prior ==="
input int    InpSeasonalYears              = 10;
input int    InpMinimumSeasonalSamples     = 5;
input double InpSeasonalReturnThresholdPct = 0.50;

input group "=== Risk and locks ==="
input double InpRiskPerTradePct             = 0.10;
input double InpMaxDailyLossPct             = 0.75;
input double InpMaxWeeklyLossPct            = 2.00;
input double InpEmergencyDrawdownPct        = 6.00;
input int    InpMaxConsecutiveLosses        = 3;
input int    InpConsecutiveLossLockHours    = 72;
input int    InpMaxTradesPerDay             = 1;
input int    InpCooldownMinutes             = 20;
input double InpMaximumMarginFraction       = 0.25;

input group "=== Stop, target and execution ==="
input double InpStopAtrBuffer               = 0.20;
input double InpMinimumStopM1Atr            = 1.20;
input double InpMaximumStopM5Atr            = 1.80;
input double InpMaxSpreadPrice              = 0.60;
input double InpMaxSpreadAtrFraction        = 0.20;
input double InpMaxSpreadStopFraction       = 0.15;
input double InpMaxEntryDriftStopFraction   = 0.10;
input int    InpDeviationPoints             = 30;

input group "=== Broker-server sessions ==="
input bool   InpEnableAsiaSession           = false;
input bool   InpEnableLondonSession         = true;
input bool   InpEnableNewYorkSession        = true;
input bool   InpUseSessionDirectionFilter   = true;
input int    InpAsiaStartHour               = 1;
input int    InpLondonStartHour             = 8;
input int    InpNewYorkStartHour            = 13;
input int    InpSessionEndHour              = 21;
input bool   InpBlockUSDataWindow           = true;
input int    InpUSDataStartHour             = 15;
input int    InpUSDataEndHour               = 17;
input int    InpFridayLastEntryHour         = 18;

input group "=== Economic calendar ==="
input bool   InpUseEconomicCalendar         = true;
input bool   InpCalendarFailClosed          = true;
input int    InpHighImpactMinutesBefore     = 45;
input int    InpHighImpactMinutesAfter      = 30;

input group "=== Diagnostics ==="
input bool   InpDiagnosticLogging           = true;
input int    InpHeartbeatMinutes            = 30;
input bool   InpNotificationOutboxEnabled   = true;
input string InpNotificationOutboxFile      = "AURUM_CENT_ADAPTIVE_M1_telegram_outbox.tsv";

int g_hH1Ema       = INVALID_HANDLE;
int g_hM15FastEma  = INVALID_HANDLE;
int g_hM15SlowEma  = INVALID_HANDLE;
int g_hM15Adx      = INVALID_HANDLE;
int g_hM15Atr      = INVALID_HANDLE;
int g_hM5Ema       = INVALID_HANDLE;
int g_hM5Atr       = INVALID_HANDLE;
int g_hM1FastEma   = INVALID_HANDLE;
int g_hM1SlowEma   = INVALID_HANDLE;
int g_hM1Atr       = INVALID_HANDLE;

datetime g_lastM1Bar       = 0;
datetime g_lastHeartbeat   = 0;
double   g_peakEquity      = 0.0;
double   g_dayStartEquity  = 0.0;
double   g_weekStartEquity = 0.0;
int      g_dayStamp        = 0;
int      g_weekStamp       = 0;
int      g_seasonYear      = 0;
int      g_seasonMonth     = 0;
int      g_seasonBias      = 0;
int      g_seasonSamples   = 0;
double   g_seasonAverage   = 0.0;
string   g_statePrefix     = "";
string   g_lastReject      = "";
datetime g_lastRejectLog   = 0;
datetime g_lastCalendarCheck = 0;
datetime g_calendarBlockedUntil = 0;
bool     g_calendarAvailable = false;
string   g_calendarBlockName = "";
bool     g_realAuthorized = false;
bool     g_notificationWriteFailed = false;
bool     g_centRiskFallbackLogged = false;

//+------------------------------------------------------------------+
//| Utility                                                          |
//+------------------------------------------------------------------+
void Diagnostic(const string message)
  {
   if(InpDiagnosticLogging)
      Print("AURUM|",message);
  }

string SanitizeNotificationField(string value)
  {
   StringReplace(value,"\t"," ");
   StringReplace(value,"\r"," ");
   StringReplace(value,"\n"," ");
   return value;
  }

void QueueNotification(const string eventName,const string message)
  {
   if(!InpNotificationOutboxEnabled || MQLInfoInteger(MQL_TESTER) || MQLInfoInteger(MQL_OPTIMIZATION))
      return;
   ResetLastError();
   int handle=FileOpen(InpNotificationOutboxFile,
                       FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ|FILE_SHARE_WRITE,
                       '\t',CP_UTF8);
   if(handle == INVALID_HANDLE)
     {
      if(!g_notificationWriteFailed)
        {
         g_notificationWriteFailed=true;
         Diagnostic(StringFormat("NOTIFY_OUTBOX_FAILED|error=%d",GetLastError()));
        }
      return;
     }
   FileSeek(handle,0,SEEK_END);
   string when=TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS);
   FileWrite(handle,SanitizeNotificationField(when),SanitizeNotificationField(eventName),
             SanitizeNotificationField(message));
   FileFlush(handle);
   FileClose(handle);
   g_notificationWriteFailed=false;
  }

void Reject(const string reason,const datetime now)
  {
   // Keep long tester and forward-demo logs useful without printing the same
   // veto on every M1 bar. A changed veto is always logged; an unchanged veto
   // is repeated every 15 minutes as a liveness sample.
   if(reason != g_lastReject || g_lastRejectLog <= 0 || now-g_lastRejectLog >= 15*60)
     {
      Diagnostic("NO_TRADE|reason="+reason);
      g_lastReject=reason;
      g_lastRejectLog=now;
     }
  }

string DirectionName(const int direction)
  {
   if(direction > 0) return "BUY";
   if(direction < 0) return "SELL";
   return "NONE";
  }

string SessionName(const ENUM_AURUM_SESSION session)
  {
   if(session == AURUM_SESSION_ASIA) return "ASIA";
   if(session == AURUM_SESSION_LONDON) return "LONDON";
   if(session == AURUM_SESSION_NEW_YORK) return "NEW_YORK";
   return "BLOCKED";
  }

string RegimeName(const ENUM_AURUM_REGIME regime)
  {
   if(regime == AURUM_REGIME_RANGE) return "RANGE";
   if(regime == AURUM_REGIME_TREND) return "TREND";
   if(regime == AURUM_REGIME_HIGH_VOLATILITY) return "HIGH_VOLATILITY";
   if(regime == AURUM_REGIME_TRANSITION) return "TRANSITION";
   return "UNKNOWN";
  }

bool ContainsHfmIdentity()
  {
   string identity=AccountInfoString(ACCOUNT_SERVER)+" "+AccountInfoString(ACCOUNT_COMPANY);
   StringToUpper(identity);
   return (StringFind(identity,"HFM") >= 0 ||
           StringFind(identity,"HF MARKETS") >= 0 ||
           StringFind(identity,"HFMARKETS") >= 0 ||
           StringFind(identity,"HOTFOREX") >= 0);
  }

bool HasCentSymbolSuffix()
  {
   int length=StringLen(_Symbol);
   if(length < 2) return false;
   string suffix=StringSubstr(_Symbol,length-1,1);
   StringToUpper(suffix);
   return suffix == "C";
  }

bool NearlyEqual(const double lhs,const double rhs,const double tolerance)
  {
   return MathAbs(lhs-rhs) <= MathMax(0.0,tolerance);
  }

bool ValidateHfmCentEnvironment(string &reason)
  {
   string currency=AccountInfoString(ACCOUNT_CURRENCY);
   if(InpRequireCentCurrency && currency != "USC")
     { reason="USC_ACCOUNT_REQUIRED|currency="+currency; return false; }
   if(!InpRequireHfmEnvironment)
      return true;
   if(!ContainsHfmIdentity())
     { reason="HFM_SERVER_REQUIRED"; return false; }
   if(!HasCentSymbolSuffix())
     { reason="HFM_CENT_SYMBOL_SUFFIX_REQUIRED"; return false; }

   double contract=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE);
   double minimum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   double maximum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   double tickSize=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   string profitCurrency=SymbolInfoString(_Symbol,SYMBOL_CURRENCY_PROFIT);
   long tradeMode=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_MODE);
   if(!NearlyEqual(contract,InpExpectedGoldContractSize,InpContractSizeTolerance))
     { reason=StringFormat("CENT_CONTRACT_MISMATCH|actual=%.4f|expected=%.4f",contract,InpExpectedGoldContractSize); return false; }
   if(!NearlyEqual(minimum,0.01,0.000001) || !NearlyEqual(step,0.01,0.000001))
     { reason=StringFormat("CENT_VOLUME_SPEC_MISMATCH|min=%.4f|step=%.4f",minimum,step); return false; }
   if(maximum < minimum || tickSize <= 0.0)
     { reason="CENT_SYMBOL_SPEC_INVALID"; return false; }
   if(profitCurrency != "USD")
     { reason="CENT_PROFIT_CURRENCY_USD_REQUIRED|currency="+profitCurrency; return false; }
   if(tradeMode != SYMBOL_TRADE_MODE_FULL && tradeMode != SYMBOL_TRADE_MODE_LONGONLY &&
      tradeMode != SYMBOL_TRADE_MODE_SHORTONLY)
     { reason=StringFormat("SYMBOL_NOT_TRADEABLE|mode=%d",tradeMode); return false; }
   return true;
  }

bool CalculateRiskMoney(const ENUM_ORDER_TYPE orderType,const double volume,
                        const double openPrice,const double closePrice,
                        double &risk,string &method)
  {
   risk=0.0;
   method="UNAVAILABLE";
   if(volume <= 0.0 || openPrice <= 0.0 || closePrice <= 0.0 ||
      MathAbs(openPrice-closePrice) <= 0.0)
      return false;

   double profit=0.0;
   if(OrderCalcProfit(orderType,_Symbol,volume,openPrice,closePrice,profit) &&
      MathIsValidNumber(profit) && MathAbs(profit) > 0.0)
     {
      risk=MathAbs(profit);
      method="ORDER_CALC_PROFIT";
      return true;
     }

   // Fail-closed fallback for the exact HFM Cent Gold contract validated by
   // the live read-only probe. It is never used for other brokers, currencies,
   // symbols, profit currencies, or contract specifications.
   if(AccountInfoString(ACCOUNT_CURRENCY) != "USC" ||
      SymbolInfoString(_Symbol,SYMBOL_CURRENCY_PROFIT) != "USD" ||
      !ContainsHfmIdentity() || !HasCentSymbolSuffix())
      return false;
   double contract=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE);
   double minimum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   if(!NearlyEqual(contract,InpExpectedGoldContractSize,InpContractSizeTolerance) ||
      !NearlyEqual(minimum,0.01,0.000001) || !NearlyEqual(step,0.01,0.000001))
      return false;

   risk=MathAbs(openPrice-closePrice)*contract*volume*100.0;
   if(!MathIsValidNumber(risk) || risk <= 0.0)
     {
      risk=0.0;
      return false;
     }
   method="USD_TO_USC_X100_FALLBACK";
   return true;
  }

bool GetBufferValue(const int handle,const int buffer,const int shift,double &value)
  {
   double values[1];
   ResetLastError();
   if(CopyBuffer(handle,buffer,shift,1,values) != 1)
      return false;
   value=values[0];
   return MathIsValidNumber(value);
  }

bool GetClosedRate(const ENUM_TIMEFRAMES timeframe,const int shift,MqlRates &rate)
  {
   MqlRates values[1];
   ResetLastError();
   if(CopyRates(_Symbol,timeframe,shift,1,values) != 1)
      return false;
   rate=values[0];
   return (rate.time > 0 && rate.high >= rate.low && rate.close > 0.0);
  }

double NormalizePrice(const double price)
  {
   double tickSize=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   int digits=(int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS);
   if(tickSize <= 0.0)
      tickSize=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   if(tickSize <= 0.0)
      return NormalizeDouble(price,digits);
   return NormalizeDouble(MathRound(price/tickSize)*tickSize,digits);
  }

int VolumeDigits(const double step)
  {
   int digits=0;
   double scaled=step;
   while(digits < 8 && MathAbs(scaled-MathRound(scaled)) > 1e-8)
     {
      scaled*=10.0;
      digits++;
     }
   return digits;
  }

double NormalizeVolumeDown(const double rawVolume)
  {
   double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   if(step <= 0.0)
      return 0.0;
   double volume=MathFloor((rawVolume+1e-12)/step)*step;
   return NormalizeDouble(volume,VolumeDigits(step));
  }

int CurrentDayStamp(const datetime when)
  {
   MqlDateTime dt;
   TimeToStruct(when,dt);
   return dt.year*1000+dt.day_of_year;
  }

int CurrentWeekStamp(const datetime when)
  {
   MqlDateTime dt;
   TimeToStruct(when,dt);
   int daysSinceMonday=(dt.day_of_week+6)%7;
   datetime monday=when-daysSinceMonday*86400-dt.hour*3600-dt.min*60-dt.sec;
   return (int)(monday/86400);
  }

datetime StartOfDay(const datetime when)
  {
   MqlDateTime dt;
   TimeToStruct(when,dt);
   dt.hour=0;
   dt.min=0;
   dt.sec=0;
   return StructToTime(dt);
  }

//+------------------------------------------------------------------+
//| Persistent equity anchors                                        |
//+------------------------------------------------------------------+
void SaveRiskState()
  {
   if(g_statePrefix == "")
      return;
   GlobalVariableSet(g_statePrefix+"PEAK",g_peakEquity);
   GlobalVariableSet(g_statePrefix+"DAYEQ",g_dayStartEquity);
   GlobalVariableSet(g_statePrefix+"WEEKEQ",g_weekStartEquity);
   GlobalVariableSet(g_statePrefix+"DAY",(double)g_dayStamp);
   GlobalVariableSet(g_statePrefix+"WEEK",(double)g_weekStamp);
  }

void LoadRiskState()
  {
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   g_dayStamp=CurrentDayStamp(now);
   g_weekStamp=CurrentWeekStamp(now);
   g_peakEquity=equity;
   g_dayStartEquity=equity;
   g_weekStartEquity=equity;

   if(GlobalVariableCheck(g_statePrefix+"PEAK"))
      g_peakEquity=GlobalVariableGet(g_statePrefix+"PEAK");
   if(GlobalVariableCheck(g_statePrefix+"DAY") &&
      (int)GlobalVariableGet(g_statePrefix+"DAY") == g_dayStamp)
      g_dayStartEquity=GlobalVariableGet(g_statePrefix+"DAYEQ");
   if(GlobalVariableCheck(g_statePrefix+"WEEK") &&
      (int)GlobalVariableGet(g_statePrefix+"WEEK") == g_weekStamp)
      g_weekStartEquity=GlobalVariableGet(g_statePrefix+"WEEKEQ");

   if(g_peakEquity <= 0.0) g_peakEquity=equity;
   if(g_dayStartEquity <= 0.0) g_dayStartEquity=equity;
   if(g_weekStartEquity <= 0.0) g_weekStartEquity=equity;
   SaveRiskState();
  }

void RefreshRiskAnchors(const datetime now)
  {
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   int day=CurrentDayStamp(now);
   int week=CurrentWeekStamp(now);
   bool changed=false;
   if(day != g_dayStamp)
     {
      g_dayStamp=day;
      g_dayStartEquity=equity;
      changed=true;
     }
   if(week != g_weekStamp)
     {
      g_weekStamp=week;
      g_weekStartEquity=equity;
      changed=true;
     }
   if(equity > g_peakEquity)
     {
      g_peakEquity=equity;
      changed=true;
     }
   if(changed) SaveRiskState();
  }

//+------------------------------------------------------------------+
//| History and exposure                                             |
//+------------------------------------------------------------------+
bool IsOwnedDeal(const ulong ticket)
  {
   if((ulong)HistoryDealGetInteger(ticket,DEAL_MAGIC) != InpMagicNumber)
      return false;
   return HistoryDealGetString(ticket,DEAL_SYMBOL) == _Symbol;
  }

int TradesOpenedToday(const datetime now)
  {
   if(!HistorySelect(StartOfDay(now),now))
      return 0;
   int count=0;
   int total=HistoryDealsTotal();
   for(int i=0;i<total;i++)
     {
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket == 0 || !IsOwnedDeal(ticket)) continue;
      long entry=HistoryDealGetInteger(ticket,DEAL_ENTRY);
      if(entry == DEAL_ENTRY_IN || entry == DEAL_ENTRY_INOUT)
         count++;
     }
   return count;
  }

datetime LastOwnedEntryTime()
  {
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   if(!HistorySelect(now-30*86400,now))
      return 0;
   for(int i=HistoryDealsTotal()-1;i>=0;i--)
     {
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket == 0 || !IsOwnedDeal(ticket)) continue;
      long entry=HistoryDealGetInteger(ticket,DEAL_ENTRY);
      if(entry == DEAL_ENTRY_IN || entry == DEAL_ENTRY_INOUT)
         return (datetime)HistoryDealGetInteger(ticket,DEAL_TIME);
     }
   return 0;
  }

int ConsecutiveOwnedLosses(datetime &lastExit)
  {
   lastExit=0;
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   if(!HistorySelect(now-180*86400,now))
      return 0;
   int losses=0;
   for(int i=HistoryDealsTotal()-1;i>=0;i--)
     {
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket == 0 || !IsOwnedDeal(ticket)) continue;
      long entry=HistoryDealGetInteger(ticket,DEAL_ENTRY);
      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY && entry != DEAL_ENTRY_INOUT)
         continue;
      datetime dealTime=(datetime)HistoryDealGetInteger(ticket,DEAL_TIME);
      if(lastExit == 0) lastExit=dealTime;
      double net=HistoryDealGetDouble(ticket,DEAL_PROFIT)
                +HistoryDealGetDouble(ticket,DEAL_SWAP)
                +HistoryDealGetDouble(ticket,DEAL_COMMISSION);
      if(net < -1e-8)
        {
         losses++;
         continue;
        }
      if(net > 1e-8)
         break;
     }
   return losses;
  }

bool HasAnySymbolExposure()
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong ticket=PositionGetTicket(i);
      if(ticket > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol)
         return true;
     }
   for(int i=OrdersTotal()-1;i>=0;i--)
     {
      ulong ticket=OrderGetTicket(i);
      if(ticket > 0 && OrderGetString(ORDER_SYMBOL) == _Symbol)
         return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Session and calendar context                                     |
//+------------------------------------------------------------------+
ENUM_AURUM_SESSION DetermineSession(const datetime now)
  {
   MqlDateTime dt;
   TimeToStruct(now,dt);
   if(InpEnableAsiaSession && dt.hour >= InpAsiaStartHour && dt.hour < InpLondonStartHour)
      return AURUM_SESSION_ASIA;
   if(InpEnableLondonSession && dt.hour >= InpLondonStartHour && dt.hour < InpNewYorkStartHour)
      return AURUM_SESSION_LONDON;
   if(InpEnableNewYorkSession && dt.hour >= InpNewYorkStartHour && dt.hour < InpSessionEndHour)
      return AURUM_SESSION_NEW_YORK;
   return AURUM_SESSION_BLOCKED;
  }

int SessionMinimumScore(const ENUM_AURUM_SESSION session)
  {
   if(session == AURUM_SESSION_ASIA) return 90;
   if(session == AURUM_SESSION_LONDON) return 82;
   if(session == AURUM_SESSION_NEW_YORK) return 85;
   return 101;
  }

double SessionRewardRisk(const ENUM_AURUM_SESSION session)
  {
   if(session == AURUM_SESSION_ASIA) return 1.20;
   if(session == AURUM_SESSION_LONDON) return 1.50;
   if(session == AURUM_SESSION_NEW_YORK) return 1.40;
   return 0.0;
  }

bool CalendarBlocksEntry(const datetime now,string &reason)
  {
   if(!InpUseEconomicCalendar)
      return false;

   // The MT5 tester has no dependable live calendar feed. Keep a conservative
   // fixed proxy there so regression tests remain deterministic.
   if(MQLInfoInteger(MQL_TESTER))
     {
      MqlDateTime dt;
      TimeToStruct(now,dt);
      if(InpBlockUSDataWindow && dt.hour >= InpUSDataStartHour && dt.hour < InpUSDataEndHour)
        { reason="US_DATA_TESTER_PROXY"; return true; }
      return false;
     }

   if(g_calendarBlockedUntil > now)
     {
      reason="USD_HIGH_IMPACT|event="+g_calendarBlockName;
      return true;
     }
   if(g_lastCalendarCheck > 0 && now-g_lastCalendarCheck < 60)
     {
      if(!g_calendarAvailable && InpCalendarFailClosed)
        { reason="ECONOMIC_CALENDAR_UNAVAILABLE"; return true; }
      return false;
     }

   g_lastCalendarCheck=now;
   g_calendarAvailable=false;
   g_calendarBlockedUntil=0;
   g_calendarBlockName="";
   datetime from=now-MathMax(0,InpHighImpactMinutesAfter)*60;
   datetime to=now+MathMax(0,InpHighImpactMinutesBefore)*60;
   MqlCalendarValue values[];
   ResetLastError();
   int total=CalendarValueHistory(values,from,to,"US","USD");
   if(total < 0)
     {
      if(InpCalendarFailClosed)
        { reason=StringFormat("ECONOMIC_CALENDAR_UNAVAILABLE|error=%d",GetLastError()); return true; }
      return false;
     }
   g_calendarAvailable=true;

   for(int i=0;i<total;i++)
     {
      MqlCalendarEvent event={};
      if(!CalendarEventById(values[i].event_id,event))
         continue;
      if(event.importance != CALENDAR_IMPORTANCE_HIGH)
         continue;
      datetime blockedFrom=values[i].time-MathMax(0,InpHighImpactMinutesBefore)*60;
      datetime blockedUntil=values[i].time+MathMax(0,InpHighImpactMinutesAfter)*60;
      if(now < blockedFrom || now > blockedUntil)
         continue;
      g_calendarBlockedUntil=blockedUntil;
      g_calendarBlockName=event.name;
      StringReplace(g_calendarBlockName,"|","/");
      reason="USD_HIGH_IMPACT|event="+g_calendarBlockName;
      return true;
     }
   return false;
  }

void RefreshSeasonalPrior(const datetime now)
  {
   MqlDateTime current;
   TimeToStruct(now,current);
   if(g_seasonYear == current.year && g_seasonMonth == current.mon)
      return;

   g_seasonYear=current.year;
   g_seasonMonth=current.mon;
   g_seasonBias=0;
   g_seasonSamples=0;
   g_seasonAverage=0.0;

   int requestedYears=MathMax(1,MathMin(InpSeasonalYears,30));
   int barsToCopy=requestedYears*370+60;
   MqlRates daily[];
   ArraySetAsSeries(daily,false);
   int copied=CopyRates(_Symbol,PERIOD_D1,1,barsToCopy,daily);
   if(copied <= 0)
     {
      Diagnostic("SEASON|status=NO_DATA");
      return;
     }

   int years[40];
   datetime firstTime[40],lastTime[40];
   double firstPrice[40],lastPrice[40];
   ArrayInitialize(years,0);
   ArrayInitialize(firstTime,0);
   ArrayInitialize(lastTime,0);
   ArrayInitialize(firstPrice,0.0);
   ArrayInitialize(lastPrice,0.0);
   int used=0;

   for(int i=0;i<copied;i++)
     {
      MqlDateTime dt;
      TimeToStruct(daily[i].time,dt);
      if(dt.mon != current.mon || dt.year >= current.year || dt.year < current.year-requestedYears)
         continue;
      int index=-1;
      for(int j=0;j<used;j++)
         if(years[j] == dt.year) { index=j; break; }
      if(index < 0 && used < 40)
        {
         index=used++;
         years[index]=dt.year;
        }
      if(index < 0) continue;
      if(firstTime[index] == 0 || daily[i].time < firstTime[index])
        {
         firstTime[index]=daily[i].time;
         firstPrice[index]=daily[i].open;
        }
      if(lastTime[index] == 0 || daily[i].time > lastTime[index])
        {
         lastTime[index]=daily[i].time;
         lastPrice[index]=daily[i].close;
        }
     }

   double sum=0.0;
   for(int i=0;i<used;i++)
     {
      if(firstPrice[i] <= 0.0 || lastPrice[i] <= 0.0) continue;
      sum+=(lastPrice[i]-firstPrice[i])/firstPrice[i];
      g_seasonSamples++;
     }
   if(g_seasonSamples > 0)
      g_seasonAverage=sum/g_seasonSamples;

   double threshold=InpSeasonalReturnThresholdPct/100.0;
   if(g_seasonSamples >= InpMinimumSeasonalSamples)
     {
      if(g_seasonAverage >= threshold) g_seasonBias=1;
      else if(g_seasonAverage <= -threshold) g_seasonBias=-1;
     }

   Diagnostic(StringFormat("SEASON|month=%d|samples=%d|avg_pct=%.3f|bias=%s",
              current.mon,g_seasonSamples,g_seasonAverage*100.0,DirectionName(g_seasonBias)));
  }

//+------------------------------------------------------------------+
//| Market model                                                     |
//+------------------------------------------------------------------+
int H1Direction()
  {
   MqlRates bar1,bar2;
   double ema1=0.0,ema2=0.0;
   if(!GetClosedRate(PERIOD_H1,1,bar1) || !GetClosedRate(PERIOD_H1,2,bar2)) return 0;
   if(!GetBufferValue(g_hH1Ema,0,1,ema1) || !GetBufferValue(g_hH1Ema,0,2,ema2)) return 0;
   if(bar1.close > ema1 && ema1 >= ema2) return 1;
   if(bar1.close < ema1 && ema1 <= ema2) return -1;
   return 0;
  }

bool AverageM15Atr(double &average)
  {
   double values[];
   ArrayResize(values,20);
   int copied=CopyBuffer(g_hM15Atr,0,1,20,values);
   if(copied < 10) return false;
   double sum=0.0;
   for(int i=0;i<copied;i++) sum+=values[i];
   average=sum/copied;
   return average > 0.0;
  }

ENUM_AURUM_REGIME M15Regime(int &direction,double &adxValue,double &atrValue)
  {
   direction=0;
   adxValue=0.0;
   atrValue=0.0;
   double fast=0.0,slow=0.0,plusDi=0.0,minusDi=0.0,averageAtr=0.0;
   if(!GetBufferValue(g_hM15FastEma,0,1,fast) ||
      !GetBufferValue(g_hM15SlowEma,0,1,slow) ||
      !GetBufferValue(g_hM15Adx,0,1,adxValue) ||
      !GetBufferValue(g_hM15Adx,1,1,plusDi) ||
      !GetBufferValue(g_hM15Adx,2,1,minusDi) ||
      !GetBufferValue(g_hM15Atr,0,1,atrValue) ||
      !AverageM15Atr(averageAtr))
      return AURUM_REGIME_UNKNOWN;

   if(atrValue > averageAtr*InpHighVolatilityMultiplier)
      return AURUM_REGIME_HIGH_VOLATILITY;
   if(adxValue < InpM15MinimumAdx)
      return AURUM_REGIME_RANGE;
   if(fast > slow && plusDi > minusDi) direction=1;
   else if(fast < slow && minusDi > plusDi) direction=-1;
   else return AURUM_REGIME_TRANSITION;
   return AURUM_REGIME_TREND;
  }

bool ValidM5Setup(const int direction,MqlRates &trigger,double &atrValue)
  {
   double ema=0.0;
   if(!GetClosedRate(PERIOD_M5,1,trigger) ||
      !GetBufferValue(g_hM5Ema,0,1,ema) ||
      !GetBufferValue(g_hM5Atr,0,1,atrValue))
      return false;
   double range=trigger.high-trigger.low;
   if(atrValue <= 0.0 || range <= 0.0) return false;
   double body=MathAbs(trigger.close-trigger.open);
   if(body/range < InpMinimumBodyFraction) return false;
   if(range < 0.30*atrValue || range > 1.50*atrValue) return false;

   if(direction > 0)
     {
      bool touched=(trigger.low <= ema+InpM5TouchAtrFraction*atrValue);
      bool reclaimed=(trigger.close > ema && trigger.close > trigger.open);
      bool closeQuality=((trigger.close-trigger.low)/range >= 0.65);
      bool notExtended=(trigger.close-ema <= 0.75*atrValue);
      return touched && reclaimed && closeQuality && notExtended;
     }
   bool touched=(trigger.high >= ema-InpM5TouchAtrFraction*atrValue);
   bool reclaimed=(trigger.close < ema && trigger.close < trigger.open);
   bool closeQuality=((trigger.high-trigger.close)/range >= 0.65);
   bool notExtended=(ema-trigger.close <= 0.75*atrValue);
   return touched && reclaimed && closeQuality && notExtended;
  }

bool ValidM1Trigger(const int direction,MqlRates &bar1,MqlRates &bar2,double &atrValue)
  {
   double fast=0.0,slow=0.0;
   if(!GetClosedRate(PERIOD_M1,1,bar1) || !GetClosedRate(PERIOD_M1,2,bar2) ||
      !GetBufferValue(g_hM1FastEma,0,1,fast) ||
      !GetBufferValue(g_hM1SlowEma,0,1,slow) ||
      !GetBufferValue(g_hM1Atr,0,1,atrValue))
      return false;
   double range=bar1.high-bar1.low;
   if(atrValue <= 0.0 || range <= 0.0) return false;
   double body=MathAbs(bar1.close-bar1.open);
   if(body/range < InpMinimumBodyFraction) return false;
   if(range < 0.35*atrValue || range > 1.80*atrValue) return false;

   if(direction > 0)
     {
      double lowerWick=MathMin(bar1.open,bar1.close)-bar1.low;
      bool sweep=(bar1.low < bar2.low && bar1.close > bar2.low && lowerWick/range >= 0.20);
      bool momentum=(bar1.close > bar2.high && bar1.low <= fast+0.10*atrValue);
      return bar1.close > bar1.open && bar1.close > fast && fast > slow && (sweep || momentum);
     }
   double upperWick=bar1.high-MathMax(bar1.open,bar1.close);
   bool sweep=(bar1.high > bar2.high && bar1.close < bar2.high && upperWick/range >= 0.20);
   bool momentum=(bar1.close < bar2.low && bar1.high >= fast-0.10*atrValue);
   return bar1.close < bar1.open && bar1.close < fast && fast < slow && (sweep || momentum);
  }

//+------------------------------------------------------------------+
//| Risk, order validation and execution                             |
//+------------------------------------------------------------------+
bool RiskLocked(string &reason)
  {
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_peakEquity > 0.0 && equity <= g_peakEquity*(1.0-InpEmergencyDrawdownPct/100.0))
     { reason="EMERGENCY_DRAWDOWN"; return true; }
   if(g_dayStartEquity > 0.0 && equity <= g_dayStartEquity*(1.0-InpMaxDailyLossPct/100.0))
     { reason="DAILY_LOSS_LOCK"; return true; }
   if(g_weekStartEquity > 0.0 && equity <= g_weekStartEquity*(1.0-InpMaxWeeklyLossPct/100.0))
     { reason="WEEKLY_LOSS_LOCK"; return true; }
   datetime lastLoss=0;
   int consecutiveLosses=ConsecutiveOwnedLosses(lastLoss);
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   if(consecutiveLosses >= InpMaxConsecutiveLosses && lastLoss > 0 &&
      now-lastLoss < InpConsecutiveLossLockHours*3600)
     { reason=StringFormat("CONSECUTIVE_LOSS_LOCK|count=%d|until=%s",consecutiveLosses,
                          TimeToString(lastLoss+InpConsecutiveLossLockHours*3600,TIME_DATE|TIME_MINUTES)); return true; }
   return false;
  }

bool BuildStops(const int direction,const ENUM_AURUM_SESSION session,
                const MqlTick &tick,const MqlRates &m1a,const MqlRates &m1b,
                const MqlRates &m5,const double atrM1,const double atrM5,
                double &entry,double &sl,double &tp,string &reason)
  {
   entry=(direction > 0 ? tick.ask : tick.bid);
   double spread=tick.ask-tick.bid;
   double point=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
   long stopsLevel=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL);
   double brokerMinimum=(double)stopsLevel*point;
   double minimumDistance=MathMax(InpMinimumStopM1Atr*atrM1,MathMax(4.0*spread,brokerMinimum));
   double buffer=InpStopAtrBuffer*atrM5;
   if(direction > 0)
     {
      double structure=MathMin(m5.low,MathMin(m1a.low,m1b.low))-buffer;
      sl=MathMin(structure,entry-minimumDistance);
     }
   else
     {
      double structure=MathMax(m5.high,MathMax(m1a.high,m1b.high))+buffer;
      sl=MathMax(structure,entry+minimumDistance);
     }
   sl=NormalizePrice(sl);
   double stopDistance=MathAbs(entry-sl);
   if(stopDistance <= 0.0 || stopDistance > InpMaximumStopM5Atr*atrM5)
     { reason="STOP_DISTANCE_INVALID"; return false; }
   if(spread > InpMaxSpreadPrice)
     { reason="SPREAD_ABSOLUTE"; return false; }
   if(atrM1 <= 0.0 || spread/atrM1 > InpMaxSpreadAtrFraction)
     { reason="SPREAD_TO_ATR"; return false; }
   if(spread/stopDistance > InpMaxSpreadStopFraction)
     { reason="SPREAD_TO_STOP"; return false; }
   double rr=SessionRewardRisk(session);
   if(rr <= 0.0)
     { reason="SESSION_RR_INVALID"; return false; }
   tp=NormalizePrice(direction > 0 ? entry+rr*stopDistance : entry-rr*stopDistance);
   entry=NormalizePrice(entry);
   if(direction > 0 && !(sl < entry && tp > entry))
     { reason="BUY_PRICES_INVALID"; return false; }
   if(direction < 0 && !(sl > entry && tp < entry))
     { reason="SELL_PRICES_INVALID"; return false; }
   return true;
  }

bool CalculateSafeVolume(const int direction,const double entry,const double sl,
                         double &volume,double &actualRisk,string &reason)
  {
   ENUM_ORDER_TYPE orderType=(direction > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   double riskMoney=equity*InpRiskPerTradePct/100.0;
   double oneLotProfit=0.0;
   string riskMethod="UNAVAILABLE";
   if(riskMoney <= 0.0 ||
      !CalculateRiskMoney(orderType,1.0,entry,sl,oneLotProfit,riskMethod))
     { reason="ORDER_CALC_PROFIT_FAILED"; return false; }
   if(riskMethod != "ORDER_CALC_PROFIT" && !g_centRiskFallbackLogged)
     {
      Diagnostic("RISK_CALC_FALLBACK|method="+riskMethod);
      g_centRiskFallbackLogged=true;
     }
   double oneLotLoss=oneLotProfit;
   if(oneLotLoss <= 0.0)
     { reason="ONE_LOT_LOSS_INVALID"; return false; }
   double rawVolume=riskMoney/oneLotLoss;
   volume=NormalizeVolumeDown(rawVolume);
   double minimum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double maximum=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   if(volume < minimum-1e-12)
     {
      double minimumLotProfit=0.0;
      double requiredRiskPct=0.0;
      string minimumRiskMethod="UNAVAILABLE";
      if(equity > 0.0 &&
         CalculateRiskMoney(orderType,minimum,entry,sl,minimumLotProfit,minimumRiskMethod))
         requiredRiskPct=minimumLotProfit/equity*100.0;
      reason=StringFormat("VOLUME_BELOW_MIN|raw=%.6f|min=%.4f|risk=%.4f|required_pct=%.3f",
                          rawVolume,minimum,riskMoney,requiredRiskPct);
      return false;
     }
   if(volume > maximum) volume=NormalizeVolumeDown(maximum);
   double normalizedProfit=0.0;
   string normalizedRiskMethod="UNAVAILABLE";
   if(!CalculateRiskMoney(orderType,volume,entry,sl,normalizedProfit,normalizedRiskMethod))
     { reason="NORMALIZED_RISK_CALC_FAILED"; return false; }
   actualRisk=normalizedProfit;
   if(actualRisk > riskMoney*1.05+1e-8)
     { reason="NORMALIZED_RISK_EXCEEDS_LIMIT"; return false; }

   double margin=0.0;
   if(!OrderCalcMargin(orderType,_Symbol,volume,entry,margin))
     { reason="ORDER_CALC_MARGIN_FAILED"; return false; }
   double freeMargin=AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   if(margin > freeMargin*InpMaximumMarginFraction)
     { reason="MARGIN_FRACTION_EXCEEDED"; return false; }
   return true;
  }

bool ResolveFillingMode(ENUM_ORDER_TYPE_FILLING &filling,string &reason)
  {
   long flags=SymbolInfoInteger(_Symbol,SYMBOL_FILLING_MODE);
   // Prefer all-or-nothing execution. IOC is accepted only when FOK is not
   // advertised. RETURN is forbidden for Market Execution symbols.
   if((flags & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
     { filling=ORDER_FILLING_FOK; return true; }
   if((flags & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
     { filling=ORDER_FILLING_IOC; return true; }
   long execution=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_EXEMODE);
   if(execution != SYMBOL_TRADE_EXECUTION_MARKET)
     { filling=ORDER_FILLING_RETURN; return true; }
   reason=StringFormat("FILLING_MODE_UNSUPPORTED|flags=%d|execution=%d",flags,execution);
   return false;
  }

bool SendMarketOrder(const int direction,const double volume,const double plannedEntry,
                     const double sl,const double tp,
                     const datetime signalTime,string &reason)
  {
   MqlTradeRequest request={};
   MqlTradeResult result={};
   MqlTradeCheckResult check={};
   MqlTick freshTick={};
   long tradeMode=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_MODE);
   if((direction > 0 && tradeMode == SYMBOL_TRADE_MODE_SHORTONLY) ||
      (direction < 0 && tradeMode == SYMBOL_TRADE_MODE_LONGONLY))
     { reason=StringFormat("DIRECTION_NOT_ALLOWED|mode=%d",tradeMode); return false; }
   if(!SymbolInfoTick(_Symbol,freshTick) || freshTick.ask <= freshTick.bid || freshTick.bid <= 0.0)
     { reason="FRESH_TICK_INVALID"; return false; }
   double freshEntry=(direction > 0 ? freshTick.ask : freshTick.bid);
   double stopDistance=MathAbs(freshEntry-sl);
   double plannedStopDistance=MathAbs(plannedEntry-sl);
   if(stopDistance <= 0.0 || plannedStopDistance <= 0.0 ||
      MathAbs(freshEntry-plannedEntry)/plannedStopDistance > InpMaxEntryDriftStopFraction)
     { reason="ENTRY_DRIFT_EXCEEDED"; return false; }
   if((direction > 0 && (sl >= freshEntry || tp <= freshEntry)) ||
      (direction < 0 && (sl <= freshEntry || tp >= freshEntry)))
     { reason="FRESH_PRICES_INVALID"; return false; }
   double freshRisk=0.0;
   ENUM_ORDER_TYPE orderType=(direction > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   string freshRiskMethod="UNAVAILABLE";
   if(!CalculateRiskMoney(orderType,volume,freshEntry,sl,freshRisk,freshRiskMethod))
     { reason="FRESH_RISK_CALC_FAILED"; return false; }
   double riskLimit=AccountInfoDouble(ACCOUNT_EQUITY)*InpRiskPerTradePct/100.0;
   if(freshRisk > riskLimit*1.05+1e-8)
     { reason=StringFormat("FRESH_RISK_EXCEEDED|risk=%.4f|limit=%.4f",freshRisk,riskLimit); return false; }

   request.action=TRADE_ACTION_DEAL;
   request.magic=InpMagicNumber;
   request.symbol=_Symbol;
   request.volume=volume;
   request.type=(direction > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   request.price=freshEntry;
   request.sl=sl;
   request.tp=tp;
   request.deviation=(ulong)MathMax(0,InpDeviationPoints);
   ENUM_ORDER_TYPE_FILLING filling=ORDER_FILLING_FOK;
   if(!ResolveFillingMode(filling,reason))
      return false;
   request.type_filling=filling;
   request.type_time=ORDER_TIME_GTC;
   request.comment=StringFormat("AURUM_M1_%s",DirectionName(direction));

   ResetLastError();
   if(!OrderCheck(request,check))
     {
      reason=StringFormat("ORDERCHECK_FAILED|retcode=%u|error=%d|comment=%s",
                          check.retcode,GetLastError(),check.comment);
      return false;
     }
   if(check.retcode != 0)
     {
      reason=StringFormat("ORDERCHECK_REJECT|retcode=%u|comment=%s",check.retcode,check.comment);
      return false;
     }

   ResetLastError();
   if(!OrderSend(request,result))
     {
      reason=StringFormat("ORDERSEND_CALL_FAILED|error=%d",GetLastError());
      return false;
     }
   if(result.retcode != TRADE_RETCODE_DONE && result.retcode != TRADE_RETCODE_PLACED &&
      result.retcode != TRADE_RETCODE_DONE_PARTIAL)
     {
      reason=StringFormat("ORDERSEND_REJECT|retcode=%u|comment=%s",result.retcode,result.comment);
      return false;
     }
   if(result.retcode == TRADE_RETCODE_DONE_PARTIAL)
     {
      Diagnostic(StringFormat("ORDER_PARTIAL|signal=%s|direction=%s|requested=%.4f|filled=%.4f|deal=%I64u|order=%I64u",
                 TimeToString(signalTime,TIME_DATE|TIME_MINUTES),DirectionName(direction),volume,
                 result.volume,result.deal,result.order));
      QueueNotification("ORDER_PARTIAL",StringFormat("%s %s requested %.4f filled %.4f",
                        _Symbol,DirectionName(direction),volume,result.volume));
      return true;
     }
   Diagnostic(StringFormat("ORDER_OK|signal=%s|direction=%s|volume=%.4f|sl=%.2f|tp=%.2f|deal=%I64u|order=%I64u",
              TimeToString(signalTime,TIME_DATE|TIME_MINUTES),DirectionName(direction),volume,sl,tp,result.deal,result.order));
   QueueNotification("ORDER_OK",StringFormat("%s %s volume %.4f SL %.2f TP %.2f",
                     _Symbol,DirectionName(direction),volume,sl,tp));
   return true;
  }

//+------------------------------------------------------------------+
//| Entry evaluation                                                 |
//+------------------------------------------------------------------+
void EvaluateClosedM1Bar(const datetime now)
  {
   ENUM_AURUM_SESSION session=DetermineSession(now);
   if(session == AURUM_SESSION_BLOCKED)
     { Reject("SESSION_BLOCKED",now); return; }

   MqlDateTime dt;
   TimeToStruct(now,dt);
   if(dt.day_of_week == 5 && dt.hour >= InpFridayLastEntryHour)
     { Reject("FRIDAY_CUTOFF",now); return; }
   string reason="";
   if(RiskLocked(reason))
     { Reject(reason,now); return; }
   if(TradesOpenedToday(now) >= InpMaxTradesPerDay)
     { Reject("DAILY_TRADE_CAP",now); return; }
   datetime lastEntry=LastOwnedEntryTime();
   if(lastEntry > 0 && now-lastEntry < InpCooldownMinutes*60)
     { Reject("COOLDOWN",now); return; }
   if(HasAnySymbolExposure())
     { Reject("SYMBOL_EXPOSURE",now); return; }
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED) || !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) ||
      !AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) || !AccountInfoInteger(ACCOUNT_TRADE_EXPERT))
     { Reject("TRADING_NOT_ALLOWED",now); return; }

   int h1Direction=H1Direction();
   if(h1Direction == 0)
     { Reject("H1_NO_BIAS",now); return; }

   int m15Direction=0;
   double adx=0.0,atrM15=0.0;
   ENUM_AURUM_REGIME regime=M15Regime(m15Direction,adx,atrM15);
   if(regime != AURUM_REGIME_TREND)
     { Reject("M15_REGIME_"+RegimeName(regime),now); return; }
   if(m15Direction != h1Direction)
     { Reject("TIMEFRAME_DIRECTION_CONFLICT",now); return; }
   if(InpUseSessionDirectionFilter &&
      ((session == AURUM_SESSION_LONDON && h1Direction < 0) ||
       (session == AURUM_SESSION_NEW_YORK && h1Direction > 0)))
     { Reject("SESSION_DIRECTION_FILTER",now); return; }

   MqlRates m5;
   double atrM5=0.0;
   if(!ValidM5Setup(h1Direction,m5,atrM5))
     { Reject("M5_SETUP_INVALID",now); return; }

   MqlRates m1a,m1b;
   double atrM1=0.0;
   if(!ValidM1Trigger(h1Direction,m1a,m1b,atrM1))
     { Reject("M1_TRIGGER_INVALID",now); return; }

   if(CalendarBlocksEntry(now,reason))
     { Reject(reason,now); return; }

   RefreshSeasonalPrior(now);
   int score=90;
   if(session == AURUM_SESSION_LONDON) score+=5;
   else if(session == AURUM_SESSION_NEW_YORK) score+=3;
   if(g_seasonBias == h1Direction) score+=5;
   else if(g_seasonBias == -h1Direction) score-=5;
   int minimumScore=SessionMinimumScore(session);
   if(score < minimumScore)
     {
      Diagnostic(StringFormat("NO_TRADE|reason=SCORE|score=%d|min=%d|season=%s",score,minimumScore,DirectionName(g_seasonBias)));
      return;
     }

   MqlTick tick={};
   if(!SymbolInfoTick(_Symbol,tick) || tick.ask <= tick.bid || tick.bid <= 0.0)
     { Reject("TICK_INVALID",now); return; }
   double entry=0.0,sl=0.0,tp=0.0;
   if(!BuildStops(h1Direction,session,tick,m1a,m1b,m5,atrM1,atrM5,entry,sl,tp,reason))
     { Reject(reason,now); return; }

   double volume=0.0,actualRisk=0.0;
   if(!CalculateSafeVolume(h1Direction,entry,sl,volume,actualRisk,reason))
     { Reject(reason,now); return; }

   Diagnostic(StringFormat("SIGNAL_APPROVED|direction=%s|session=%s|regime=%s|score=%d|adx=%.2f|season=%s|volume=%.4f|risk=%.4f",
              DirectionName(h1Direction),SessionName(session),RegimeName(regime),score,adx,
              DirectionName(g_seasonBias),volume,actualRisk));
   QueueNotification("SIGNAL_APPROVED",StringFormat("%s %s session %s ADX %.2f risk %.4f",
                     _Symbol,DirectionName(h1Direction),SessionName(session),adx,actualRisk));
   if(!SendMarketOrder(h1Direction,volume,entry,sl,tp,m1a.time,reason))
     {
      Diagnostic("ORDER_FAILED|reason="+reason);
      QueueNotification("ORDER_FAILED",_Symbol+" "+reason);
     }
  }

void MaybeHeartbeat(const datetime now)
  {
   if(InpHeartbeatMinutes <= 0) return;
   if(g_lastHeartbeat > 0 && now-g_lastHeartbeat < InpHeartbeatMinutes*60) return;
   g_lastHeartbeat=now;
   MqlTick tick={};
   SymbolInfoTick(_Symbol,tick);
   Diagnostic(StringFormat("HEARTBEAT|server=%s|equity=%.2f|currency=%s|spread=%.2f|session=%s|real_authorized=%s",
              TimeToString(now,TIME_DATE|TIME_SECONDS),AccountInfoDouble(ACCOUNT_EQUITY),
              AccountInfoString(ACCOUNT_CURRENCY),tick.ask-tick.bid,SessionName(DetermineSession(now)),
              (g_realAuthorized ? "true" : "false")));
  }

//+------------------------------------------------------------------+
//| MT5 event handlers                                               |
//+------------------------------------------------------------------+
int OnInit()
  {
   ENUM_ACCOUNT_TRADE_MODE accountMode=(ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   long accountLogin=AccountInfoInteger(ACCOUNT_LOGIN);
   g_realAuthorized=false;
   if(accountMode == ACCOUNT_TRADE_MODE_REAL)
     {
      if(!BUILD_ALLOW_REAL_ACCOUNT || !InpAllowRealAccount)
        { Print("AURUM|INIT_FAIL|reason=REAL_ACCOUNT_RUNTIME_LOCK"); return INIT_FAILED; }
      if(InpAuthorizedRealLogin <= 0 || accountLogin != InpAuthorizedRealLogin)
        { Print("AURUM|INIT_FAIL|reason=REAL_ACCOUNT_LOGIN_NOT_AUTHORIZED"); return INIT_FAILED; }
      if(!InpRequireHfmEnvironment)
        { Print("AURUM|INIT_FAIL|reason=HFM_VALIDATION_MANDATORY_ON_REAL"); return INIT_FAILED; }
      if(!InpRequireCentCurrency)
        { Print("AURUM|INIT_FAIL|reason=CENT_CURRENCY_VALIDATION_MANDATORY_ON_REAL"); return INIT_FAILED; }
      if(!InpUseEconomicCalendar || !InpCalendarFailClosed)
        { Print("AURUM|INIT_FAIL|reason=CALENDAR_FAIL_CLOSED_MANDATORY_ON_REAL"); return INIT_FAILED; }
      if(MathAbs(InpRiskPerTradePct-0.10) > 0.000001 || InpMaxTradesPerDay != 1 ||
         InpEnableAsiaSession || !InpUseSessionDirectionFilter || InpM15MinimumAdx < 30.0)
        { Print("AURUM|INIT_FAIL|reason=RELEASE_PROFILE_REQUIRED_ON_REAL"); return INIT_FAILED; }
      g_realAuthorized=true;
     }
   if(_Period != PERIOD_M1)
     {
      Print("AURUM|INIT_FAIL|reason=ATTACH_TO_M1");
      return INIT_FAILED;
     }
   string upper=_Symbol;
   StringToUpper(upper);
   if(StringFind(upper,"XAU") < 0 && StringFind(upper,"GOLD") < 0)
     {
      Print("AURUM|INIT_FAIL|reason=GOLD_SYMBOL_REQUIRED");
      return INIT_FAILED;
     }
   string currency=AccountInfoString(ACCOUNT_CURRENCY);
   string environmentReason="";
   if(!ValidateHfmCentEnvironment(environmentReason))
     {
      Print("AURUM|INIT_FAIL|reason=",environmentReason);
      return INIT_FAILED;
     }
   if(InpRiskPerTradePct <= 0.0 || InpRiskPerTradePct > 0.25)
     {
      Print("AURUM|INIT_FAIL|reason=RISK_OUT_OF_DEVELOPMENT_RANGE");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpMaxTradesPerDay < 1 || InpMaxTradesPerDay > 3 ||
      InpMaxDailyLossPct <= 0.0 || InpMaxDailyLossPct > 1.0 ||
      InpMaxWeeklyLossPct < InpMaxDailyLossPct || InpMaxWeeklyLossPct > 3.0 ||
      InpEmergencyDrawdownPct < InpMaxWeeklyLossPct || InpEmergencyDrawdownPct > 8.0 ||
      InpMaxConsecutiveLosses < 1 || InpMaxConsecutiveLosses > 5 ||
      InpConsecutiveLossLockHours < 1 || InpConsecutiveLossLockHours > 24*30 ||
      InpMaximumMarginFraction <= 0.0 || InpMaximumMarginFraction > 0.25 ||
      InpStopAtrBuffer < 0.0 || InpStopAtrBuffer > 1.0 ||
      InpMinimumStopM1Atr <= 0.0 || InpMinimumStopM1Atr > 3.0 ||
      InpMaximumStopM5Atr <= 0.0 || InpMaximumStopM5Atr > 5.0 ||
      InpMaxSpreadPrice <= 0.0 || InpMaxSpreadAtrFraction <= 0.0 ||
      InpMaxSpreadAtrFraction > 0.50 || InpMaxSpreadStopFraction <= 0.0 ||
      InpMaxSpreadStopFraction > 0.25 || InpMaxEntryDriftStopFraction <= 0.0 ||
      InpMaxEntryDriftStopFraction > 0.25 || InpDeviationPoints < 0 || InpDeviationPoints > 1000 ||
      InpExpectedGoldContractSize <= 0.0 || InpContractSizeTolerance < 0.0 ||
      InpHighImpactMinutesBefore < 0 || InpHighImpactMinutesBefore > 240 ||
      InpHighImpactMinutesAfter < 0 || InpHighImpactMinutesAfter > 240 ||
      InpUSDataStartHour < 0 || InpUSDataStartHour > 23 ||
      InpUSDataEndHour < 1 || InpUSDataEndHour > 24 || InpUSDataStartHour >= InpUSDataEndHour ||
      InpFridayLastEntryHour < 0 || InpFridayLastEntryHour > 23 ||
      InpAsiaStartHour < 0 || InpSessionEndHour > 24 ||
      !(InpAsiaStartHour < InpLondonStartHour && InpLondonStartHour < InpNewYorkStartHour && InpNewYorkStartHour < InpSessionEndHour))
     {
      Print("AURUM|INIT_FAIL|reason=INPUT_RANGE_INVALID");
      return INIT_PARAMETERS_INCORRECT;
     }

   g_hH1Ema=iMA(_Symbol,PERIOD_H1,InpH1EmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM15FastEma=iMA(_Symbol,PERIOD_M15,InpM15FastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM15SlowEma=iMA(_Symbol,PERIOD_M15,InpM15SlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM15Adx=iADX(_Symbol,PERIOD_M15,InpM15AdxPeriod);
   g_hM15Atr=iATR(_Symbol,PERIOD_M15,InpAtrPeriod);
   g_hM5Ema=iMA(_Symbol,PERIOD_M5,InpM5EmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM5Atr=iATR(_Symbol,PERIOD_M5,InpAtrPeriod);
   g_hM1FastEma=iMA(_Symbol,PERIOD_M1,InpM1FastEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM1SlowEma=iMA(_Symbol,PERIOD_M1,InpM1SlowEmaPeriod,0,MODE_EMA,PRICE_CLOSE);
   g_hM1Atr=iATR(_Symbol,PERIOD_M1,InpAtrPeriod);
   if(g_hH1Ema == INVALID_HANDLE || g_hM15FastEma == INVALID_HANDLE ||
      g_hM15SlowEma == INVALID_HANDLE || g_hM15Adx == INVALID_HANDLE ||
      g_hM15Atr == INVALID_HANDLE || g_hM5Ema == INVALID_HANDLE ||
      g_hM5Atr == INVALID_HANDLE || g_hM1FastEma == INVALID_HANDLE ||
      g_hM1SlowEma == INVALID_HANDLE || g_hM1Atr == INVALID_HANDLE)
     {
      Print("AURUM|INIT_FAIL|reason=INDICATOR_HANDLE");
      return INIT_FAILED;
     }

   g_statePrefix=StringFormat("AURUM.%I64d.%I64u.%s.",accountLogin,InpMagicNumber,_Symbol);
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   if(MQLInfoInteger(MQL_TESTER))
     {
      double equity=AccountInfoDouble(ACCOUNT_EQUITY);
      g_dayStamp=CurrentDayStamp(now);
      g_weekStamp=CurrentWeekStamp(now);
      g_peakEquity=equity;
      g_dayStartEquity=equity;
      g_weekStartEquity=equity;
      SaveRiskState();
     }
   else
      LoadRiskState();
   RefreshSeasonalPrior(now);
   g_lastM1Bar=iTime(_Symbol,PERIOD_M1,0);
   Diagnostic(StringFormat("BROKER_SPEC|server=%s|company=%s|contract=%.4f|min_lot=%.4f|step=%.4f|tick_size=%.5f|tick_value=%.5f",
              AccountInfoString(ACCOUNT_SERVER),AccountInfoString(ACCOUNT_COMPANY),
              SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE),
              SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN),SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP),
              SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE),SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE)));
   Diagnostic(StringFormat("INIT_OK|symbol=%s|period=M1|currency=%s|balance=%.2f|risk_pct=%.2f|min_lot=%.4f|real_authorized=%s",
              _Symbol,currency,AccountInfoDouble(ACCOUNT_BALANCE),InpRiskPerTradePct,
              SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN),(g_realAuthorized ? "true" : "false")));
   QueueNotification("INIT_OK",StringFormat("%s M1 currency %s balance %.2f real_authorized %s",
                     _Symbol,currency,AccountInfoDouble(ACCOUNT_BALANCE),(g_realAuthorized ? "true" : "false")));
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   SaveRiskState();
   if(g_hH1Ema != INVALID_HANDLE) IndicatorRelease(g_hH1Ema);
   if(g_hM15FastEma != INVALID_HANDLE) IndicatorRelease(g_hM15FastEma);
   if(g_hM15SlowEma != INVALID_HANDLE) IndicatorRelease(g_hM15SlowEma);
   if(g_hM15Adx != INVALID_HANDLE) IndicatorRelease(g_hM15Adx);
   if(g_hM15Atr != INVALID_HANDLE) IndicatorRelease(g_hM15Atr);
   if(g_hM5Ema != INVALID_HANDLE) IndicatorRelease(g_hM5Ema);
   if(g_hM5Atr != INVALID_HANDLE) IndicatorRelease(g_hM5Atr);
   if(g_hM1FastEma != INVALID_HANDLE) IndicatorRelease(g_hM1FastEma);
   if(g_hM1SlowEma != INVALID_HANDLE) IndicatorRelease(g_hM1SlowEma);
   if(g_hM1Atr != INVALID_HANDLE) IndicatorRelease(g_hM1Atr);
   Diagnostic(StringFormat("DEINIT|reason=%d",reason));
   QueueNotification("DEINIT",StringFormat("%s reason %d",_Symbol,reason));
  }

void OnTick()
  {
   datetime now=TimeTradeServer();
   if(now <= 0) now=TimeCurrent();
   RefreshRiskAnchors(now);
   MaybeHeartbeat(now);

   datetime currentM1=iTime(_Symbol,PERIOD_M1,0);
   if(currentM1 <= 0 || currentM1 == g_lastM1Bar)
      return;
   g_lastM1Bar=currentM1;
   EvaluateClosedM1Bar(now);
  }

void OnTradeTransaction(const MqlTradeTransaction &transaction,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(transaction.type != TRADE_TRANSACTION_DEAL_ADD || transaction.deal == 0)
      return;
   if(!HistoryDealSelect(transaction.deal) || !IsOwnedDeal(transaction.deal))
      return;
   long entry=HistoryDealGetInteger(transaction.deal,DEAL_ENTRY);
   double net=HistoryDealGetDouble(transaction.deal,DEAL_PROFIT)
             +HistoryDealGetDouble(transaction.deal,DEAL_SWAP)
             +HistoryDealGetDouble(transaction.deal,DEAL_COMMISSION);
   Diagnostic(StringFormat("DEAL_AUDIT|deal=%I64u|entry=%d|volume=%.4f|price=%.5f|net=%.4f|sl=%.5f|tp=%.5f",
              transaction.deal,entry,transaction.volume,transaction.price,net,transaction.price_sl,transaction.price_tp));
   QueueNotification("DEAL_AUDIT",StringFormat("%s entry %d volume %.4f price %.5f net %.4f",
                     _Symbol,entry,transaction.volume,transaction.price,net));
  }
