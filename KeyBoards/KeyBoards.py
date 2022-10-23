from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

main_menu_KeyBoard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

main_menu_KeyBoard.add("View all profiles")
main_menu_KeyBoard.add("View my likes")
main_menu_KeyBoard.add("My profile")

change_anket_menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

change_anket_menu.add("Edit photo")
change_anket_menu.add("Edit Description")
change_anket_menu.add("Cancel")

show_ankets_KeyBoard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

show_ankets_KeyBoard.add("Next")
show_ankets_KeyBoard.add("Like")
show_ankets_KeyBoard.add("Cancel")


admin_KeyBoard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

admin_KeyBoard.add("Hello")
admin_KeyBoard.add("Change login information")
admin_KeyBoard.add("Cancel")

end_anekets_KeyBoard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
end_anekets_KeyBoard.add("View old profiles")
end_anekets_KeyBoard.add("Cancel")

next_anket = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
next_anket.add(InlineKeyboardMarkup(text="next", callback_data="next"))
next_anket.add(InlineKeyboardMarkup(text="like", callback_data="like"))
