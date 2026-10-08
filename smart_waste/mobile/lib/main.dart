import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const SmartWasteApp());
}

class SmartWasteApp extends StatelessWidget {
  const SmartWasteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartWaste Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF10B981),
        scaffoldBackgroundColor: const Color(0xFF0B0F19),
        cardColor: const Color(0xFF111827),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF10B981),
          secondary: Color(0xFF3B82F6),
          surface: Color(0xFF111827),
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  final String apiBaseUrl = "http://10.0.2.2:8000"; // Android emulator or LAN IP

  final List<Widget> _screens = [
    const HomeScreen(),
    const ScanAuditScreen(),
    const BinsMonitorScreen(),
    const AuditHistoryScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF111827),
        selectedItemColor: const Color(0xFF10B981),
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.camera_alt_rounded), label: 'Scan'),
          BottomNavigationBarItem(icon: Icon(Icons.delete_outline_rounded), label: 'Bins'),
          BottomNavigationBarItem(icon: Icon(Icons.history_rounded), label: 'Audits'),
        ],
      ),
    );
  }
}

// 1. Home Dashboard
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SmartWaste Auditing', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF111827),
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            children: [
              _buildKpiCard('Efficiency', '87.4%', Icons.check_circle, Colors.green),
              const SizedBox(width: 12),
              _buildKpiCard('Contamination', '12.6%', Icons.warning, Colors.amber),
            ],
          ),
          const SizedBox(height: 16),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('AI Source Segregation', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  const Text('Take a photo of waste before disposal to verify the correct bin.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                  const SizedBox(height: 14),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      minimumSize: const Size.fromHeight(45),
                    ),
                    onPressed: () {},
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Launch Auditor Scanner'),
                  )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKpiCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF111827),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white10),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

// 2. Scan & Audit Screen
class ScanAuditScreen extends StatefulWidget {
  const ScanAuditScreen({super.key});

  @override
  State<ScanAuditScreen> createState() => _ScanAuditScreenState();
}

class _ScanAuditScreenState extends State<ScanAuditScreen> {
  File? _imageFile;
  Map<String, dynamic>? _prediction;
  bool _loading = false;
  String? _selectedBin;
  final picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    final picked = await picker.pickImage(source: source);
    if (picked != null) {
      setState(() {
        _imageFile = File(picked.path);
        _prediction = null;
        _loading = true;
      });
      _classifyWaste(_imageFile!);
    }
  }

  Future<void> _classifyWaste(File file) async {
    try {
      final req = http.MultipartRequest('POST', Uri.parse('http://127.0.0.1:8000/api/waste/predict'));
      req.files.add(await http.MultipartFile.fromPath('file', file.path));
      final res = await req.send();
      final resBody = await res.stream.bytesToString();
      final data = jsonDecode(resBody);
      setState(() {
        _prediction = data;
        _selectedBin = data['recommended_bin'];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan & Audit Waste'), backgroundColor: const Color(0xFF111827)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_imageFile != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(_imageFile!, height: 200, width: double.infinity, fit: BoxFit.cover),
              ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera),
                    label: const Text('Camera'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                  ),
                ),
              ],
            ),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(color: Color(0xFF10B981)),
              ),
            if (_prediction != null) ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Text(_prediction!['waste_class'].toString().toUpperCase(),
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    Text('Confidence: ${(_prediction!['confidence'] * 100).toStringAsFixed(1)}%',
                        style: const TextStyle(color: Color(0xFF10B981))),
                    const SizedBox(height: 8),
                    Text('Recommended: ${_prediction!['recommended_bin']}',
                        style: const TextStyle(fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}

// 3. Bins Monitor Screen
class BinsMonitorScreen extends StatelessWidget {
  const BinsMonitorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Campus Smart Bins'), backgroundColor: const Color(0xFF111827)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(title: Text('BIN-001 (Recyclable)'), subtitle: Text('Block A • 82% Full'), trailing: Text('HIGH', style: TextStyle(color: Colors.amber))),
          ListTile(title: Text('BIN-003 (Organic)'), subtitle: Text('Food Court • 94% Full'), trailing: Text('CRITICAL', style: TextStyle(color: Colors.red))),
        ],
      ),
    );
  }
}

// 4. Audit History Screen
class AuditHistoryScreen extends StatelessWidget {
  const AuditHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Audit History'), backgroundColor: const Color(0xFF111827)),
      body: const Center(child: Text('Synchronized Audit Ledger')),
    );
  }
}
