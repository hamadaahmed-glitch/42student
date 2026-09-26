/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test_ft_strlen.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: cadet <cadet@42.fr>                        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 12:05:00 by cadet             #+#    #+#             */
/*   Updated: 2026/09/26 12:05:00 by cadet            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "student42_assert.h"
#include <stddef.h>

/* Declaration of student function */
size_t ft_strlen(const char *s);

int main(void)
{
	setup_signal_traps();

	TEST_START("Empty String")
		ASSERT_EQ_INT(ft_strlen(""), 0, "ft_strlen on empty string returns 0");
	TEST_END();

	TEST_START("Standard String")
		ASSERT_EQ_INT(ft_strlen("hello"), 5, "ft_strlen on 'hello' returns 5");
	TEST_END();

	TEST_START("42 Network String")
		ASSERT_EQ_INT(ft_strlen("42"), 2, "ft_strlen on '42' returns 2");
	TEST_END();

	TEST_START("Long String")
		char long_buf[1001];
		memset(long_buf, 'a', 1000);
		long_buf[1000] = '\0';
		ASSERT_EQ_INT(ft_strlen(long_buf), 1000, "ft_strlen on 1000-char string");
	TEST_END();

	TEST_SUMMARY();
	return (0);
}