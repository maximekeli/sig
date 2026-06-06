import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFF0D2818);
  static const Color accent = Color(0xFFC9A962);
  static const Color surface = Color(0xFF1A3D2E);
  static const Color card = Color(0xFF243D32);

  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: const ColorScheme.dark(
          primary: accent,
          secondary: Color(0xFF4ADE80),
          surface: surface,
          onPrimary: primary,
          onSurface: Colors.white,
        ),
        scaffoldBackgroundColor: primary,
        appBarTheme: const AppBarTheme(
          backgroundColor: surface,
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        cardTheme: CardTheme(
          color: card,
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: card,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        navigationBarTheme: NavigationBarThemeData(
          backgroundColor: surface,
          indicatorColor: accent.withValues(alpha: 0.25),
          labelTextStyle: WidgetStateProperty.all(
            const TextStyle(fontSize: 11),
          ),
        ),
      );
}
