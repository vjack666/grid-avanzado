from datetime import datetime
import MetaTrader5 as mt5

class RiskBotMT5:
    def __init__(self, risk_target_profit, max_profit_target, risk_percent, comision_por_lote):
        self.risk_target_profit = risk_target_profit
        self.max_profit_target = max_profit_target
        self.risk_percent = risk_percent
        self.comision_por_lote = comision_por_lote

    def get_account_balance(self):
        account_info = mt5.account_info()
        if account_info:
            return account_info.balance
        return 0.0

    def get_total_profit_and_lots(self):
        positions = mt5.positions_get()
        if positions is None or len(positions) == 0:
            return 0.0, 0.0, 0.0, 0.0

        total_profit = 0.0
        total_commission = 0.0
        total_lots = 0.0

        for pos in positions:
            total_profit += pos.profit
            total_commission += pos.commission
            total_lots += pos.volume

        profit_neto = total_profit - total_commission
        return total_profit, total_commission, profit_neto, total_lots

    def check_and_act(self):
        total_profit, total_commission, profit_neto, total_lots = self.get_total_profit_and_lots()

        # Usamos datetime naive para evitar errores
        tiempo_actual = datetime.now().replace(tzinfo=None)

        if profit_neto >= self.max_profit_target:
            return 'objetivo_maximo'
        elif profit_neto >= self.risk_target_profit:
            return 'objetivo_parcial'
        elif profit_neto <= -abs(self.risk_target_profit * (self.risk_percent / 100)):
            return 'riesgo'
        else:
            return 'ok'

    def get_open_positions(self):
        """Obtiene todas las posiciones abiertas"""
        positions = mt5.positions_get()
        return positions if positions is not None else []
