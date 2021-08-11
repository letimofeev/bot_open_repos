from settings import FileName, UserStatus, UserCallbackKey, AnswerKey, AnswerValue, TextToAnswer
from settings import logger


class Answerer:
    def __init__(self, answer_config, platform_config):
        self.User = answer_config.user
        self.Messages = answer_config.messages
        self.Links = answer_config.links
        self.Schedule = answer_config.schedule
        self.RequestHandler = answer_config.request_handler
        self.GraphBuilder = answer_config.graph_builder
        self.Filter = answer_config.filter
        self.Keyboard = platform_config.keyboard
        self.TableName = platform_config.table_name
        self.KeyboardName = platform_config.keyboard_name
        self.admins = platform_config.settings.ADMINS

    def registration(self, peer_id: int, text: str) -> dict:
        text = text.lower()

        if not self.User(self.TableName, peer_id).get_reg_info():
            self.User(self.TableName, peer_id).registration()
            self.User(self.TableName, peer_id).set_status(status=UserStatus.REG_COURSE)
            logger.debug("registration(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.REG_COURSE)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_COURSE_GREETING,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.COURSES)
            }

        if text == TextToAnswer.CHANGE_REG_INFO and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.REG_COURSE)
            logger.debug("registration(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.REG_COURSE)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_COURSE_CHANGING,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.COURSES)
            }

        if self.User(self.TableName, peer_id).get_status() == UserStatus.REG_COURSE:
            if text in self.Messages().get_courses():
                self.User(self.TableName, peer_id).set_status(
                    status=UserStatus.REG_GROUP,
                    callback={UserCallbackKey.COURSE_NAME: text}
                )
                logger.debug("registration(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.REG_GROUP)
                return {
                    AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_GROUP,
                    AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.GROUPS[text])
                }

            logger.debug("registration(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.REG_COURSE)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_COURSE_TO_CONTINUE,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.COURSES)
            }

        if self.User(self.TableName, peer_id).get_status() == UserStatus.REG_GROUP:
            course_name = self.User(self.TableName, peer_id).get_callback().get(UserCallbackKey.COURSE_NAME)
            if text in self.Messages().get_groups(course_name):
                self.User(self.TableName, peer_id).registration(course=course_name, group=text)
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("registration(): user_id %s, message '%s', return reg end", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.REG_FINISH}

            logger.debug("registration(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.REG_GROUP)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_GROUP_TO_CONTINUE,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.GROUPS[course_name])
            }

        logger.debug("registration(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def answer_teacher_info(self, peer_id: int, text: str) -> dict:
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("answer_teacher_info(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()
        prefix_size = len(TextToAnswer.GET_TEACHER_INGO)

        if text[:prefix_size] == TextToAnswer.GET_TEACHER_INGO and peer_id in self.admins:
            phrase = text[prefix_size:]
            res = self.User(self.TableName).get_teacher_info(phrase)
            if res is not None:
                user_id, name, surname, answer = res
                logger.debug("answer_teacher_info(): user_id %s, message '%s', return teacher info", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.TEACHER_INFO.format(name, surname, user_id, answer)}

            logger.debug("answer_teacher_info(): user_id %s, message '%s', return answer is not set", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.ANSWER_NOT_SET}

        logger.debug("answer_teacher_info(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_text(self, peer_id: int, text: str) -> dict:
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("get_answer_text(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()

        if answer_command := self.Messages(self.TableName).get_answer_command(text):
            logger.debug("get_answer_text(): user_id %s, message '%s', return command", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: answer_command}

        if answer_custom := self.Messages(self.TableName).get_answer_custom(text):
            logger.debug("get_answer_text(): user_id %s, message '%s', return custom", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: answer_custom}

        logger.debug("get_answer_text(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_photo(self, peer_id: int, text: str) -> dict:
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("get_answer_photo(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()

        if answer := self.Messages(self.TableName).get_answer_photo(text):
            logger.debug("get_answer_photo(): user_id %s, message '%s', return photo link", peer_id, text)
            return {AnswerKey.PHOTO_LINK: answer}

        logger.debug("get_answer_photo(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_links(self, peer_id: int, text: str) -> dict:
        text = text.lower()

        if text == TextToAnswer.LECTURES and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.LINK)
            course_name, group_name = self.User(self.TableName, peer_id).get_reg_info()
            logger.debug("get_answer_links(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.LINK)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_SUBJECT,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.LECTURES[course_name])
            }

        if self.User(self.TableName, peer_id).get_status() == UserStatus.LINK:
            course_name, group_name = self.User(self.TableName, peer_id).get_reg_info()
            if text in self.Links(FileName.LINKS[course_name]).get_subj_list():
                link = self.Links(FileName.LINKS[course_name]).get_subj_link(text)
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("get_answer_links(): user_id %s, message '%s', return link", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: link}

            logger.debug("get_answer_links(): user_id %s, message '%s' wrong input, return empty", peer_id, text)
            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
            return {}

        logger.debug("get_answer_links(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_schedule(self, peer_id: int, text: str) -> dict:
        text = text.lower()

        if text == TextToAnswer.SCHEDULE and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.SCHEDULE)
            logger.debug("get_answer_schedule(): user_id %s return days", peer_id)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_DAY,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.DAYS)
            }

        if self.User(self.TableName, peer_id).get_status() == UserStatus.SCHEDULE:
            course_name, group_name = self.User(self.TableName, peer_id).get_reg_info()
            if text in self.Messages().get_days():
                day_schedule = self.Schedule(FileName.SCHEDULE, course_name, group_name).get_schedule_str(text)
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("get_answer_schedule(): user_id %s, message '%s', return schedule", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: day_schedule}

            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
            logger.debug("get_answer_schedule(): user_id %s, message '%s' wrong input, return empty", peer_id, text)
            return {}

        logger.debug("get_answer_schedule(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def delete_answer(self, peer_id: int, text: str) -> dict:
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("delete_answer(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()
        prefix_size = len(TextToAnswer.DELETE_CUSTOM)

        if text[:prefix_size] == TextToAnswer.DELETE_CUSTOM and peer_id in self.admins:
            phrase = text[prefix_size:]
            if self.Messages(self.TableName).get_answer_custom(phrase):
                self.Messages(self.TableName).delete_answer_custom(phrase)
                logger.debug("delete_answer(): user_id %s, message '%s', return answer deleted", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_DELETED.format(phrase)}

            logger.debug("delete_answer(): user_id %s, message '%s', return answer is not set", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.ANSWER_NOT_SET}

        logger.debug("delete_answer(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_other_materials(self, peer_id, text):
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("get_other_materials(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()

        if text == TextToAnswer.OTHER_MATERIALS:
            logger.debug("get_other_materials(): user_id %s, message '%s', return link", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.OTHER_MATERIALS}

        logger.debug("get_other_materials(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def switch_menu(self, peer_id, text):
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("switch_menu(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()

        if text == TextToAnswer.SECOND_MENU:
            logger.debug("switch_menu(): user_id %s, message '%s', return second menu", peer_id, text)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.OTHER_FUNC,
                AnswerKey.DEFAULT_KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.START["start2"])
            }

        if text == TextToAnswer.RETURN_MAIN_MENU:
            logger.debug("switch_menu(): user_id %s, message '%s', return main menu", peer_id, text)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.MAIN_MENU,
                AnswerKey.DEFAULT_KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.START["start1"])
            }

        logger.debug("switch_menu(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_query(self, peer_id: int, text: str) -> dict:
        if text.lower() == TextToAnswer.QUERY and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.QUERY)
            logger.debug("get_answer_query(): user_id %s, message '%s', return input query", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.INPUT_QUERY}

        if self.User(self.TableName, peer_id).get_status() == UserStatus.QUERY:
            if answer := self.RequestHandler().get_response(text):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("get_answer_query(): user_id %s, message '%s', return query answer", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: answer}

            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
            logger.debug("get_answer_query(): user_id %s, message '%s', return answer not found", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.QUERY_FAILED}

        logger.debug("get_answer_query(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer_graph(self, peer_id: int, text: str) -> dict:
        if text.lower() == TextToAnswer.GRAPH and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.VAR_NUM)
            logger.debug("get_answer_graph(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.VAR_NUM)
            return {
                AnswerKey.TEXT_ANSWER: AnswerValue.CHOOSE_VAR_NUM,
                AnswerKey.KEYBOARD: self.Keyboard.json_to_keyboard(self.KeyboardName.VAR_NUM)
            }

        if self.User(self.TableName, peer_id).get_status() == UserStatus.VAR_NUM:
            text = text.lower()
            if var_num := self.Messages().get_var_num(text):
                self.User(self.TableName, peer_id).set_status(
                    status=UserStatus.FUNC,
                    callback={UserCallbackKey.VAR_NUM: var_num}
                )
                logger.debug("get_answer_graph(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.FUNC)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.INPUT_FUNC}

            logger.debug("get_answer_graph(): user_id %s, message '%s', return wrong var num", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.WRONG_VAR_NUM}

        if self.User(self.TableName, peer_id).get_status() == UserStatus.FUNC:
            var_num = self.User(self.TableName, peer_id).get_callback().get(UserCallbackKey.VAR_NUM)
            if self.GraphBuilder().save_plot(func=text, var_num=var_num, graph_name=FileName.GRAPH):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("get_answer_graph(): user_id %s, message '%s', return graph", peer_id, text)
                return {AnswerKey.PHOTO_FILE: FileName.GRAPH}

            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
            logger.debug("get_answer_graph(): user_id %s, message '%s', return graph failed", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.GRAPH_FAILED}

        logger.debug("get_answer_graph(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def ban(self, peer_id: int, text: str) -> dict:
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("ban(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()
        prefix_size = len(TextToAnswer.BAN)
        if text[:prefix_size] == TextToAnswer.BAN and peer_id in self.admins:
            user_id = text[prefix_size:]
            self.User(self.TableName, user_id).ban()
            logger.debug("ban(): user_id %s, message '%s', return banned", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.BANNED}

        logger.debug("ban(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def unban(self, peer_id, text):
        if (user_status := self.User(self.TableName, peer_id).get_status()) != UserStatus.ANY:
            logger.debug("unban(): user_id %s, status %s, return empty", peer_id, user_status)
            return {}

        text = text.lower()
        prefix_size = len("unban ")
        if text[:prefix_size] == "unban " and peer_id in self.admins:
            user_id = text[prefix_size:]
            if self.User(self.TableName, user_id).ban_check():
                self.User(self.TableName, user_id).unban()
                logger.debug("ban(): user_id %s, message '%s', return unbanned", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.UNBANNED}

            logger.debug("ban(): user_id %s, message '%s', return was not banned", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.WAS_NOT_BANNED}

        logger.debug("ban(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def teach_bot(self, peer_id: int, text: str) -> dict:
        if text.lower() == TextToAnswer.TEACH and self.User(self.TableName, peer_id).get_status() == UserStatus.ANY:
            self.User(self.TableName, peer_id).set_status(UserStatus.CUSTOM_TO_ANSWER)
            logger.debug("teach_bot(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.CUSTOM_TO_ANSWER)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_TO_ANSWER}

        if self.User(self.TableName, peer_id).get_status() == UserStatus.CUSTOM_TO_ANSWER:
            if not self.Filter(FileName.FILTER).is_allowed(text):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("teach_bot(): user_id %s, message '%s', return filter reject", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_FILTER_REJECT}

            if self.Messages().is_reserved(text.lower()):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("teach_bot(): user_id %s, message '%s', return reserved reject", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_RESERVED_REJECT}

            if self.Messages(self.TableName).get_answer_custom(text.lower()):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("teach_bot(): user_id %s, message '%s', return already taught reject", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_TAUGHT_REJECT}

            self.User(self.TableName, peer_id).set_status(
                status=UserStatus.CUSTOM_ANSWER,
                callback={UserCallbackKey.CUSTOM_TO_ANSWER: text.lower()}
            )
            logger.debug("teach_bot(): user_id %s, message '%s', status '%s'", peer_id, text, UserStatus.CUSTOM_ANSWER)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_ANSWER}

        if self.User(self.TableName, peer_id).get_status() == UserStatus.CUSTOM_ANSWER:
            if not self.Filter(FileName.FILTER).is_allowed(text):
                self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
                logger.debug("teach_bot(): user_id %s, message '%s', return filter reject", peer_id, text)
                return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_FILTER_REJECT}

            self.Messages(self.TableName).add_answer_custom(
                user_id=peer_id,
                text=self.User(self.TableName, peer_id).get_callback().get(UserCallbackKey.CUSTOM_TO_ANSWER),
                answer=text
            )
            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)
            logger.debug("teach_bot(): user_id %s, message '%s', return custom end", peer_id, text)
            return {AnswerKey.TEXT_ANSWER: AnswerValue.CUSTOM_FINISH}

        logger.debug("teach_bot(): user_id %s, message '%s', return empty", peer_id, text)
        return {}

    def get_answer(self, peer_id, text):
        if self.User(self.TableName, peer_id).get_status() is None:
            self.User(self.TableName, peer_id).set_status(status=UserStatus.ANY)

        if answer_registration := self.registration(peer_id, text):
            return answer_registration

        if answer_text := self.get_answer_text(peer_id, text):
            return answer_text

        if answer_teacher_info := self.answer_teacher_info(peer_id, text):
            return answer_teacher_info

        if answer_photo := self.get_answer_photo(peer_id, text):
            return answer_photo

        if answer_teach := self.teach_bot(peer_id, text):
            return answer_teach

        if answer_links := self.get_answer_links(peer_id, text):
            return answer_links

        if answer_schedule := self.get_answer_schedule(peer_id, text):
            return answer_schedule

        if answer_query := self.get_answer_query(peer_id, text):
            return answer_query

        if other := self.get_other_materials(peer_id, text):
            return other

        if switch := self.switch_menu(peer_id, text):
            return switch

        if answer_graph := self.get_answer_graph(peer_id, text):
            return answer_graph

        if answer_ban := self.ban(peer_id, text):
            return answer_ban

        if answer_unban := self.unban(peer_id, text):
            return answer_unban

        if answer_delete_text := self.delete_answer(peer_id, text):
            return answer_delete_text

        return {}
