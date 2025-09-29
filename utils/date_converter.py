from datetime import datetime, date
import jdatetime
from typing import Optional

class DateConverter:
    @staticmethod
    def gregorian_to_jalali(gregorian_date: date) -> jdatetime.date:
        """Convert Gregorian date to Jalali date"""
        return jdatetime.date.fromgregorian(date=gregorian_date)
    
    @staticmethod
    def jalali_to_gregorian(jalali_date: jdatetime.date) -> date:
        """Convert Jalali date to Gregorian date"""
        return jalali_date.togregorian()
    
    @staticmethod
    def gregorian_to_jalali_str(gregorian_date: date, format_str: str = "%Y/%m/%d") -> str:
        """Convert Gregorian date to Jalali string"""
        jalali_date = DateConverter.gregorian_to_jalali(gregorian_date)
        return jalali_date.strftime(format_str)
    
    @staticmethod
    def jalali_str_to_gregorian(jalali_str: str, format_str: str = "%Y/%m/%d") -> date:
        """Convert Jalali string to Gregorian date"""
        jalali_date = jdatetime.datetime.strptime(jalali_str, format_str)
        return jalali_date.togregorian()
    
    @staticmethod
    def get_current_jalali_date() -> jdatetime.date:
        """Get current Jalali date"""
        return jdatetime.date.today()
    
    @staticmethod
    def get_current_jalali_date_str(format_str: str = "%Y/%m/%d") -> str:
        """Get current Jalali date as string"""
        return jdatetime.date.today().strftime(format_str)
    
    @staticmethod
    def get_jalali_month_name(month_number: int) -> str:
        """Get Jalali month name"""
        months = {
            1: "فروردین",
            2: "اردیبهشت",
            3: "خرداد",
            4: "تیر",
            5: "مرداد",
            6: "شهریور",
            7: "مهر",
            8: "آبان",
            9: "آذر",
            10: "دی",
            11: "بهمن",
            12: "اسفند"
        }
        return months.get(month_number, "")