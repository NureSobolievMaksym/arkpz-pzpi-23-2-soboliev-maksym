import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartClimate',
      theme: ThemeData(primarySwatch: Colors.teal, useMaterial3: true),
      home: const LoginScreen(),
    );
  }
}

// ---------------- LOGIN SCREEN ----------------
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Для Android емулятора використовуй 10.0.2.2. Для Linux/Web - localhost
  final String apiUrl = "http://localhost:8000"; 
  final _userController = TextEditingController(text: "user1");
  final _passController = TextEditingController(text: "password");
  String? _error;

  Future<void> _login() async {
    try {
      final res = await http.post(
        Uri.parse('$apiUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "username": _userController.text,
          "password": _passController.text
        }),
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (ctx) => UserDashboard(userId: data['id'])),
        );
      } else {
        setState(() => _error = "Invalid credentials");
      }
    } catch (e) {
      setState(() => _error = "Connection error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_circle, size: 80, color: Colors.teal),
            const SizedBox(height: 20),
            TextField(controller: _userController, decoration: const InputDecoration(labelText: "Username", border: OutlineInputBorder())),
            const SizedBox(height: 10),
            TextField(controller: _passController, obscureText: true, decoration: const InputDecoration(labelText: "Password", border: OutlineInputBorder())),
            const SizedBox(height: 20),
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            ElevatedButton(onPressed: _login, child: const Text("Login")),
          ],
        ),
      ),
    );
  }
}

// ---------------- USER DASHBOARD ----------------
class UserDashboard extends StatefulWidget {
  final int userId;
  const UserDashboard({super.key, required this.userId});
  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
  final String apiUrl = "http://localhost:8000";
  List<dynamic> devices = [];
  Timer? timer;

  @override
  void initState() {
    super.initState();
    _fetchDevices();
    timer = Timer.periodic(const Duration(seconds: 2), (t) => _fetchDevices());
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchDevices() async {
    // В ідеалі треба спочатку отримати Home, потім Room, потім Device.
    // Для демо ми зробимо спрощений запит, отримавши Всі девайси і відфільтрувавши їх (якщо бекенд дозволяє)
    // Або просто покажемо статистику по Дому ID=1 (як MVP)
    
    // Тут ми імітуємо отримання пристроїв для простоти (в Swagger є GET /devices/)
    try {
      final res = await http.get(Uri.parse('$apiUrl/devices/')); // Цей ендпоінт повертає всі, треба фільтрувати на беку
      if (res.statusCode == 200) {
        if(mounted) {
          setState(() {
            devices = jsonDecode(res.body); // У реальному проекті фільтрувати по owner_id
          });
        }
      }
    } catch (e) {
      debugPrint("Error loading devices");
    }
  }
  
  Future<void> _addDevice() async {
      // Логіка додавання пристрою (аналог POST /devices/)
      // Можна відкрити діалогове вікно
      await http.post(
          Uri.parse('$apiUrl/devices/'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
              "name": "New Sensor",
              "device_type": "THERMOSTAT",
              "mac_address": "AA:BB:CC:${DateTime.now().millisecond}",
              "room_id": 1 // Hardcoded room for demo
          })
      );
      _fetchDevices();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("My Devices"), actions: [
        IconButton(icon: const Icon(Icons.add), onPressed: _addDevice)
      ]),
      body: devices.isEmpty 
        ? const Center(child: Text("No devices found. Try adding one."))
        : ListView.builder(
            itemCount: devices.length,
            itemBuilder: (ctx, i) {
              final dev = devices[i];
              return _buildDeviceCard(dev);
            },
          ),
    );
  }

  Widget _buildDeviceCard(dynamic dev) {
    // Отримуємо останні вимірювання (якщо є в об'єкті, інакше треба окремий запит)
    // Припустимо, що бекенд поки не повертає measurement всередині device list,
    // тому зробимо запит на /devices/{id}/measurements для відображення
    
    return FutureBuilder(
      future: http.get(Uri.parse('$apiUrl/devices/${dev['id']}/measurements')),
      builder: (ctx, snapshot) {
        String statusText = "No data";
        String temp = "--";
        
        if (snapshot.hasData && snapshot.data!.statusCode == 200) {
            List measures = jsonDecode(snapshot.data!.body);
            if (measures.isNotEmpty) {
                var last = measures.last;
                temp = "${last['temperature']}°C";
                statusText = "Updated: ${last['timestamp']}";
            }
        }
        
        return Card(
          margin: const EdgeInsets.all(8),
          child: ListTile(
            leading: Icon(Icons.thermostat, color: Colors.teal, size: 40),
            title: Text(dev['name']),
            subtitle: Text(statusText),
            trailing: Text(temp, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          ),
        );
      },
    );
  }
}