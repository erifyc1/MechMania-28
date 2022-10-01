import zipapp
print("Writing to bot.pyz...")
zipapp.create_archive('.', main='main:main', target='bot3.pyz')
print("Done!")