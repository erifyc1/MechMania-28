import zipapp
print("Writing to bot.pyz...")
zipapp.create_archive('.', main='main:main', target='bot4.pyz')
print("Done!")