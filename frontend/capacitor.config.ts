import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.campusfix.app',
  appName: '校修通',
  webDir: 'dist',
  server: {
    cleartext: true,
    androidScheme: 'https',
  },
  android: {
    allowMixedContent: true,
    buildOptions: {
      keystorePath: '',
      keystorePassword: '',
      keystoreAlias: '',
      keystoreAliasPassword: '',
    },
  },
};

export default config;
