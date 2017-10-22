from distutils.core import setup
import setup_translate

pkg = 'Extensions.FallbackReceiver'
setup (name = 'enigma2-plugin-extensions-fallbackreceiver',
       version = '1.05',
       description = 'set fallback remote receiver from editable list',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
