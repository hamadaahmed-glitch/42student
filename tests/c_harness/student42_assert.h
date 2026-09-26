/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   student42_assert.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: cadet <cadet@42.fr>                        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 12:00:00 by cadet             #+#    #+#             */
/*   Updated: 2026/09/26 12:00:00 by cadet            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STUDENT42_ASSERT_H
# define STUDENT42_ASSERT_H

# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <signal.h>
# include <setjmp.h>
# include <unistd.h>

static int g_tests_run = 0;
static int g_tests_passed = 0;
static int g_tests_failed = 0;
static jmp_buf g_jump_buf;
static const char *g_current_test_name = "";

static void sigsegv_handler(int sig)
{
	(void)sig;
	printf("{\"test\": \"%s\", \"passed\": false, \"signal\": \"SIGSEGV\"}\n", g_current_test_name);
	g_tests_failed++;
	longjmp(g_jump_buf, 1);
}

static void sigabrt_handler(int sig)
{
	(void)sig;
	printf("{\"test\": \"%s\", \"passed\": false, \"signal\": \"SIGABRT\"}\n", g_current_test_name);
	g_tests_failed++;
	longjmp(g_jump_buf, 1);
}

static void setup_signal_traps(void)
{
	signal(SIGSEGV, sigsegv_handler);
	signal(SIGABRT, sigabrt_handler);
}

# define TEST_START(name) do { \
	g_current_test_name = name; \
	g_tests_run++; \
	if (setjmp(g_jump_buf) == 0) {

# define TEST_END() \
	} \
} while (0)

# define ASSERT_TRUE(condition, desc) do { \
	if (condition) { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": true}\n", g_current_test_name, desc); \
		g_tests_passed++; \
	} else { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": false, \"error\": \"Assertion failed\"}\n", g_current_test_name, desc); \
		g_tests_failed++; \
	} \
} while (0)

# define ASSERT_EQ_INT(actual, expected, desc) do { \
	int _act = (int)(actual); \
	int _exp = (int)(expected); \
	if (_act == _exp) { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": true}\n", g_current_test_name, desc); \
		g_tests_passed++; \
	} else { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": false, \"expected\": %d, \"actual\": %d}\n", g_current_test_name, desc, _exp, _act); \
		g_tests_failed++; \
	} \
} while (0)

# define ASSERT_STR_EQ(actual, expected, desc) do { \
	const char *_act = (const char *)(actual); \
	const char *_exp = (const char *)(expected); \
	if ((_act == NULL && _exp == NULL) || (_act && _exp && strcmp(_act, _exp) == 0)) { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": true}\n", g_current_test_name, desc); \
		g_tests_passed++; \
	} else { \
		printf("{\"test\": \"%s\", \"desc\": \"%s\", \"passed\": false, \"expected\": \"%s\", \"actual\": \"%s\"}\n", \
			g_current_test_name, desc, _exp ? _exp : "NULL", _act ? _act : "NULL"); \
		g_tests_failed++; \
	} \
} while (0)

# define TEST_SUMMARY() do { \
	printf("{\"summary\": {\"run\": %d, \"passed\": %d, \"failed\": %d}}\n", \
		g_tests_run, g_tests_passed, g_tests_failed); \
	if (g_tests_failed > 0) \
		exit(1); \
	else \
		exit(0); \
} while (0)

#endif