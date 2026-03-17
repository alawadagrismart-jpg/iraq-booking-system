import React, { useState, useRef } from 'react';
import { 
  StyleSheet, 
  View, 
  Text, 
  TouchableOpacity, 
  SafeAreaView, 
  Modal, 
  ScrollView, 
  StatusBar, 
  ActivityIndicator,
  Dimensions
} from 'react-native';
// استيراد WebView الحقيقي (يجب تثبيته عبر: npm install react-native-webview)
import { WebView } from 'react-native-webview';
// استيراد الأيقونات المتوافقة مع React Native
import { 
  Plus, 
  Trash2, 
  Zap, 
  ShieldCheck, 
  Smartphone, 
  X, 
  RefreshCcw, 
  Lock 
} from 'lucide-react-native';

const { width, height } = Dimensions.get('window');

// --- نظام توليد البصمات التقنية (Technical Spoofing Logic) ---
const generateSpoofProfile = () => {
  const androidVersions = ['11', '12', '13', '14'];
  const devices = [
    { brand: 'Samsung', model: 'SM-S918B', build: 'TP1A.220624.014' },
    { brand: 'Google', model: 'Pixel 7 Pro', build: 'TD1A.220804.031' },
    { brand: 'Xiaomi', model: '2210132G', build: 'TKQ1.220829.002' },
    { brand: 'Huawei', model: 'VOG-L29', build: 'HUAWEIVOG-L29' }
  ];

  const device = devices[Math.floor(Math.random() * devices.length)];
  const version = androidVersions[Math.floor(Math.random() * androidVersions.length)];
  
  // توليد User-Agent يطابق التطبيق الرسمي بدقة
  const userAgent = `Mozilla/5.0 (Linux; Android ${version}; ${device.model} Build/${device.build}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36 [com.moi.ayniq]`;

  return {
    id: Math.random().toString(36).substring(7),
    brand: device.brand,
    model: device.model,
    userAgent: userAgent,
    androidVersion: version,
    headers: {
      "X-Requested-With": "com.moi.ayniq", // المفتاح التقني للتمويه
      "Accept-Language": "ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    }
  };
};

const App = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const webViewRef = useRef(null);

  const startNewSession = () => {
    setLoading(true);
    setTimeout(() => {
      const newProfile = generateSpoofProfile();
      setSessions(prev => [newProfile, ...prev]);
      setActiveSession(newProfile);
      setLoading(false);
    }, 1200);
  };

  const deleteSession = (id) => {
    setSessions(prev => prev.filter(item => item.id !== id));
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" />
      
      {/* Header - شريط الرأس */}
      <View style={styles.header}>
        <View style={styles.headerTextGroup}>
          <Text style={styles.headerTitle}>نظام التمويه</Text>
          <Text style={styles.headerSubtitle}>VIRTUAL SPOOFING ENGINE</Text>
        </View>
        <ShieldCheck color="#EAB308" size={28} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* New Identity Button */}
        <TouchableOpacity 
          style={styles.mainButton} 
          onPress={startNewSession}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#000" />
          ) : (
            <View style={styles.buttonRow}>
              <Plus color="#000" size={24} strokeWidth={3} />
              <Text style={styles.buttonText}>تخليق هوية "شبح" جديدة</Text>
            </View>
          )}
        </TouchableOpacity>

        <Text style={styles.sectionLabel}>الجلسات النشطة</Text>

        {sessions.map((s) => (
          <View key={s.id} style={styles.sessionCard}>
            <View style={styles.cardTop}>
              <View style={styles.deviceInfo}>
                <View style={styles.iconBg}>
                  <Smartphone color="#EAB308" size={20} />
                </View>
                <View>
                  <Text style={styles.deviceName}>{s.brand} {s.model}</Text>
                  <Text style={styles.deviceVer}>Android {s.androidVersion}</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => deleteSession(s.id)}>
                <Trash2 color="#444" size={20} />
              </TouchableOpacity>
            </View>

            <View style={styles.metaData}>
              <Lock color="#555" size={12} />
              <Text style={styles.metaText} numberOfLines={1}>ID: {s.id.toUpperCase()} | HEADER: com.moi.ayniq</Text>
            </View>

            <TouchableOpacity 
              style={styles.launchButton} 
              onPress={() => setActiveSession(s)}
            >
              <Zap color="#EAB308" size={16} fill="#EAB308" />
              <Text style={styles.launchText}>بدء الحقن والدخول</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>

      {/* WebView Modal - نافذة المتصفح الحقيقية */}
      <Modal 
        visible={activeSession !== null} 
        animationType="slide" 
        onRequestClose={() => setActiveSession(null)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setActiveSession(null)} style={styles.closeBtn}>
              <X color="#fff" size={24} />
            </TouchableOpacity>
            <View style={styles.modalStatus}>
              <Text style={styles.modalTitle}>متصفح التمويه النشط</Text>
              <Text style={styles.modalUrl}>ayniraq.moi.gov.iq</Text>
            </View>
            <RefreshCcw color="#555" size={20} />
          </View>

          {activeSession && (
            <WebView 
              ref={webViewRef}
              source={{ 
                uri: 'https://ayniraq.moi.gov.iq/',
                headers: activeSession.headers 
              }}
              userAgent={activeSession.userAgent}
              style={styles.webview}
              incognito={true} // وضع التخفي
              domStorageEnabled={true}
              javaScriptEnabled={true}
              startInLoadingState={true}
              renderLoading={() => (
                <View style={styles.webLoader}>
                  <ActivityIndicator color="#EAB308" size="large" />
                  <Text style={styles.webLoaderText}>جاري حقن البصمة التقنية...</Text>
                </View>
              )}
            />
          )}
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#050505',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
    gap: 12,
  },
  headerTextGroup: {
    alignItems: 'flex-end',
  },
  headerTitle: {
    color: '#EAB308',
    fontSize: 20,
    fontWeight: '900',
  },
  headerSubtitle: {
    color: '#444',
    fontSize: 9,
    fontWeight: 'bold',
  },
  scrollContent: {
    padding: 20,
  },
  mainButton: {
    backgroundColor: '#EAB308',
    borderRadius: 20,
    padding: 20,
    marginBottom: 30,
    shadowColor: '#EAB308',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.2,
    shadowRadius: 15,
    elevation: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  buttonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '900',
  },
  sectionLabel: {
    color: '#555',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'right',
    marginBottom: 15,
    marginRight: 5,
  },
  sessionCard: {
    backgroundColor: '#0f0f0f',
    borderRadius: 24,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  cardTop: {
    flexDirection: 'row-reverse',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  deviceInfo: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: 12,
  },
  iconBg: {
    backgroundColor: '#1a1a1a',
    padding: 10,
    borderRadius: 12,
  },
  deviceName: {
    color: '#eee',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'right',
  },
  deviceVer: {
    color: '#555',
    fontSize: 10,
    textAlign: 'right',
  },
  metaData: {
    backgroundColor: '#000',
    borderRadius: 12,
    padding: 10,
    flexDirection: 'row-reverse',
    alignItems: 'center',
    gap: 8,
    marginBottom: 15,
  },
  metaText: {
    color: '#EAB308',
    fontSize: 9,
    fontFamily: 'monospace',
  },
  launchButton: {
    backgroundColor: '#EAB30815',
    padding: 14,
    borderRadius: 15,
    flexDirection: 'row-reverse',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
    borderWidth: 1,
    borderColor: '#EAB30830',
  },
  launchText: {
    color: '#EAB308',
    fontSize: 13,
    fontWeight: '900',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#0a0a0a',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  closeBtn: {
    padding: 5,
  },
  modalStatus: {
    alignItems: 'center',
  },
  modalTitle: {
    color: '#EAB308',
    fontSize: 12,
    fontWeight: '900',
  },
  modalUrl: {
    color: '#444',
    fontSize: 9,
  },
  webview: {
    flex: 1,
    backgroundColor: '#000',
  },
  webLoader: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  webLoaderText: {
    color: '#EAB308',
    marginTop: 20,
    fontSize: 12,
    fontWeight: 'bold',
  }
});

export default App;
